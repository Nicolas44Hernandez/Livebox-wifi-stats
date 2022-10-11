"""
Retrieve stats from stations connected to the 2.4 GHz and 5 GHz frequency band by ussing the commands:
* wl -i wl0 assoclist
* wl info_sta
"""

from datetime import datetime, timedelta
import logging
import time
from common.telnet import Telnet
import yaml

logger = logging.getLogger(__name__)

RESULTS_FILE_CONNECTIONS_NUMBER =  "connections_number.txt"
# File name will be completed with the station number info_station{i}.txt
RESULTS_FILE_INFO_STATION =  "station_"

COMMANDS = {
    "get header": "echo -e \"connected    2.4GHz    5GHz    datetime\"",
    "check if 5GHz band is up": 'wl -i wl0 bss',
    "check if 2.4GHz band is up": 'wl -i wl2 bss',
    "get stations MAC list 5GHz": "echo -n 'EE''EE '; wl -i wl0 assoclist | sed 's/assoclist //'; echo 'FF''FF'",
    "get stations MAC list 2.4GHz": "echo -n 'EE''EE '; wl -i wl2 assoclist | sed 's/assoclist //'; echo 'FF''FF'",
    "get station info": "echo -n 'EE''EE '; wl sta_info MAC_ADDRESS; echo 'FF''FF'",
    "check if file exists": "echo -n 'EE''EE '; test -f FILE && echo 'exists'; echo 'FF''FF'",
}

def get_columns(config_file: str):
    """Get results file columns from config file"""

    # Read yml config file
    with open(config_file, "r") as stream:
        try:
            parsed_yaml = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error(exc)

    # Extract data
    columns = parsed_yaml["COLUMNS"]

    return columns

def check_if_results_file_exists(telnet: Telnet, file: str):
    """Check if result file already exists"""

    check_if_file_exists_command = COMMANDS["check if file exists"].replace("FILE", file)
    telnet.send_command(check_if_file_exists_command)
    _result_brut = telnet.connection.read_until(b"FFFF").decode('ascii')
    result= str(parse_telnet_output(_result_brut))
    return "exists" in result

def write_single_station_info(
    telnet: Telnet,
    columns_conf: str,
    mac_addr: str,
    wifi_band: str,
    date_time: str,
    results_dir:str
    ):

    """
    Append station info to dedicated result file, if the file doenst exists creates a file with the headers
    """

    formatted_mac = mac_addr.replace(":", "_")
    file_name = f"{results_dir}/{RESULTS_FILE_INFO_STATION}{formatted_mac}.txt"
    output_redirection_command = f" >> {file_name}"

    # get table columns
    columns = get_columns(config_file=columns_conf)

    if not check_if_results_file_exists(telnet=telnet, file=file_name):
        header = ""
        for i, col in enumerate(columns):
            if i != 0:
                header += "    "
            header += col
        # add wifiband and datetime
        header = f"{header}    band_wifi    date_time"

        # Write header
        write_header_command = f"echo '{header}' {output_redirection_command}"
        telnet.send_command(write_header_command)

    # retrieve station info
    sta_info_command =  COMMANDS["get station info"].replace("MAC_ADDRESS", mac_addr)
    telnet.send_command(sta_info_command)
    station_info_result_brut = telnet.connection.read_until(b"FFFF").decode('ascii')
    _raw_station_info= str(parse_telnet_output(station_info_result_brut)).split("\r\n")[1:-1]

    # create entry
    new_entry = ""
    for i, col in enumerate(columns):
        for line in _raw_station_info:
            if col in line:
                value = line.split(col)[1][1:].replace("= ", "")
                if i != 0:
                    new_entry += "    "
                new_entry += f"{value}"
                continue

    if new_entry == "":
        return

    # add wifiband and datetime
    new_entry = f"{new_entry}    {wifi_band}    {date_time}"
    # Write entry
    write_stations_info_command = f"echo -e \"{new_entry}\" {output_redirection_command}"
    telnet.send_command(write_stations_info_command)

def write_stations_info_in_file(
    telnet: Telnet,
    results_dir: str,
    connections_2_4GHz: int,
    connections_5GHz: int,
    columns_conf: str,
    ):
    """Loop over connected stations and write stats in results files"""

    date_time = str(datetime.now())
    # loop over stations connected to 2.4GHz band
    for station in connections_2_4GHz:
        write_single_station_info(
            telnet=telnet,
            columns_conf=columns_conf,
            mac_addr=station,
            wifi_band="2.4GHz",
            date_time=date_time,
            results_dir=results_dir
        )
    # loop over stations connected to 5GHZ band
    for station in connections_5GHz:
        write_single_station_info(
            telnet=telnet,
            columns_conf=columns_conf,
            mac_addr=station,
            wifi_band="5GHz",
            date_time=date_time,
            results_dir=results_dir
        )

def write_nb_connections_in_file(
    telnet: Telnet,
    results_dir: str,
    connections_number: int,
    connections_2_4GHz: int,
    connections_5GHz: int
    ):
    """
    Write the number of connected stations for each band in the dedicated results file
    """

    # redirection to file command
    output_redirection_command = " >> " + results_dir + "/" + RESULTS_FILE_CONNECTIONS_NUMBER

    # Write connected stations command
    date_time = str(datetime.now())


    # create entry
    new_entry = f"{connections_number}    {connections_5GHz}    {connections_2_4GHz}    {date_time}"
    # Write entry
    write_connected_stations_command = f"echo -e \"{new_entry}\" {output_redirection_command}"
    # Send command
    telnet.send_command(write_connected_stations_command)

def parse_telnet_output(raw_output: str):
    """Parse the output of the sent command"""
    _splitted_patern = raw_output.split("EEEE")
    return _splitted_patern[len(_splitted_patern) -1].split("FFFF")[0].lstrip()

def get_connected_stations_in_band(telnet: Telnet, band: str):
    """Returns the MAC list of stations connected to the band WiFi"""
    # Input check
    if band not in ["2.4GHz","5GHz"]:
        return []

    telnet.send_command(COMMANDS["get stations MAC list " + band]) # # @MAC => # connected stations
    mac_list_result_brut = telnet.connection.read_until(b"FFFF").decode('ascii')
    _raw_mac_list= str(parse_telnet_output(mac_list_result_brut))
    if len(_raw_mac_list) == 0:
        return []
    connected_stations = _raw_mac_list.split("\r\n")[:-1]
    logger.info(f'Stations conected to band %s: %s', band, str(connected_stations))
    return connected_stations

def get_connected_stations(telnet: Telnet):
    """Retrive the list of mac addresses of the stations connected to each frequency band"""
    # Get connected stations
    connected_stations_5GHz= []
    connected_stations_2_4GHz= get_connected_stations_in_band(telnet, "2.4GHz")
    # check if 5GHz band is up
    if band_is_up(telnet, "5GHz"):
        connected_stations_5GHz = get_connected_stations_in_band(telnet, "5GHz")
    total_connections = len(connected_stations_2_4GHz) + len(connected_stations_5GHz)
    logger.info(f"total_connections={total_connections}  2.4GHz:{connected_stations_2_4GHz}  5GHz:{connected_stations_5GHz}")

    return total_connections, connected_stations_2_4GHz, connected_stations_5GHz

def band_is_up(telnet: Telnet, band: str):
    """Check if a frequency band is up or down"""
    # Input check
    if band not in ["2.4GHz","5GHz"]:
        return False

    # clean output
    telnet.connection.read_very_eager()
    # execute command
    telnet.send_command(COMMANDS["check if " + band + " band is up"])
    # get ret value
    ret_val = telnet.connection.read_until(b"#").decode('ascii')
    band_is_up = not "down" in ret_val
    # clean output
    telnet.connection.read_very_eager()
    return band_is_up

def run_info_connected_stations(
    telnet: Telnet,
    results_dir:str,
    analysis_duration_in_minutes: int,
    sampling_period_in_seconds: int,
    columns_config_file: str
):
    """Entry point for info connected stations program"""

    logger.info("RUNNING PROGRAM: stations info")

    start = datetime.now()
    estimated_end = start + timedelta(minutes=analysis_duration_in_minutes)
    logger.info(f"Estimated end: {str(estimated_end)}")

    # Write header
    output_redirection_command = " >> " + results_dir + "/" + RESULTS_FILE_CONNECTIONS_NUMBER
    write_header_command = COMMANDS['get header'] + output_redirection_command
    telnet.send_command(write_header_command)

    # Waiting loop
    now = datetime.now()
    while now < estimated_end:
        next_sample_at = now + timedelta(seconds=sampling_period_in_seconds)

        # Get number of connected stations
        total_connections, connected_stations_2_4GHz, connected_stations_5GHz = get_connected_stations(telnet)
        logger.info(f"Connected stations: {total_connections} 2.4GHz band: {connected_stations_2_4GHz} 5GHz band: {connected_stations_5GHz}")

        # Write number of connections in dedicated file
        write_nb_connections_in_file(
            telnet=telnet,
            results_dir=results_dir,
            connections_number=total_connections,
            connections_2_4GHz=len(connected_stations_2_4GHz),
            connections_5GHz=len(connected_stations_5GHz),
        )
        if total_connections > 0 :
            write_stations_info_in_file(
                telnet=telnet,
                results_dir=results_dir,
                connections_2_4GHz=connected_stations_2_4GHz,
                connections_5GHz=connected_stations_5GHz,
                columns_conf=columns_config_file,
            )
        now = datetime.now()

        while now < next_sample_at:
            time.sleep(0.1)
            now = datetime.now()



