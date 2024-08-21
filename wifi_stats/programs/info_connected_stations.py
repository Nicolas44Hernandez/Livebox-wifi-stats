"""
Retrieve stats from stations connected to the 2.4 GHz and 5 GHz frequency bands
Stats are logged in result files
"""

from datetime import datetime, timedelta
import logging
import time
import os
from common import SshClient
import yaml

logger = logging.getLogger(__name__)

RESULTS_FILE_CONNECTIONS_NUMBER = "connections_number.txt"
# File name will be completed with the station number info_station{i}.txt
RESULTS_FILE_INFO_STATION = "station_"

COMMANDS = {
    "get active stations in BAND": "WiFi.AccessPoint.BAND.AssociatedDevice.*.Active",
    "get station data": "WiFi.AccessPoint.BAND.AssociatedDevice.INDEX.",
    "check if band is up": "WiFi.Radio.RADIO.Status",
}

BANDS = {"2.4GHz":"2", "5GHz": "1"}
RADIO = {"2.4GHz":"1", "5GHz": "2"}


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

def write_single_station_info(
    ssh: SshClient,
    columns_conf: str,
    station: dict,
    wifi_band: str,
    date_time: str,
    results_dir: str
):
    """
    Append station info to dedicated result file, if the file doenst exists creates a file with the headers
    """
    mac_address = station["MACAddress"].replace("\"", "")
    formatted_mac = mac_address.replace(":", "_")
    file_name = f"{results_dir}/{RESULTS_FILE_INFO_STATION}{formatted_mac}.txt"

    # get table columns
    columns = get_columns(config_file=columns_conf)

    # Create station results file if doesnt exist and append header
    file_exists = os.path.isfile(file_name)
    if not file_exists:
        try:
            with open(file_name, 'x') as file:
                header = ""
                for key in columns:
                    header+=f"{key}\t"
                header+=f"wifi-band\tdatetime\n"
                file.write(header)
                logger.info(f"{file_name} results file created")
        except FileExistsError:
            logger.info(f"The file '{file_name}' already exists.")

    # Create new entry with station info
    with open(file_name, 'a') as file:
        new_entry = ""
        for key in columns:
            if key in station:
                new_entry += f"{station[key]}\t"
            else:
                new_entry += f"None\t"
        new_entry += f"{wifi_band}\t{date_time}\n"
        # Append new entry to file
        file.write(new_entry)


def write_stations_info_in_file(
    ssh: SshClient,
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
            ssh=ssh,
            columns_conf=columns_conf,
            station=station,
            wifi_band="2.4GHz",
            date_time=date_time,
            results_dir=results_dir
        )
    # loop over stations connected to 5GHZ band
    for station in connections_5GHz:
        write_single_station_info(
            ssh=ssh,
            columns_conf=columns_conf,
            station=station,
            wifi_band="5GHz",
            date_time=date_time,
            results_dir=results_dir
        )


def write_nb_connections_in_file(
    ssh: SshClient,
    results_file: str,
    connections_number: int,
    connections_2_4GHz: int,
    connections_5GHz: int
):
    """
    Write the number of connected stations for each band in the dedicated results file
    """
    # Write connected stations info
    date_time = str(datetime.now())

    # create entry
    new_entry = f"{connections_number}    {connections_5GHz}    {connections_2_4GHz}    {date_time}\n"
    # Write entry
    try:
        with open(results_file, 'a') as file:
            file.write(new_entry)
    except Exception:
        logger.error(f"Error when appending to results file")

def parse_telnet_output(raw_output: str):
    """Parse the output of the sent command"""
    _splitted_patern = raw_output.split("EEEE")
    return _splitted_patern[len(_splitted_patern) - 1].split("FFFF")[0].lstrip()


def get_connected_stations_in_band(ssh: SshClient, band: str):
    """Returns the MAC list of stations connected to the band WiFi"""
    # Input check
    if band not in BANDS:
        return []

    # initialize
    active_stations = []

    # Get indexes of active stations
    cmd = COMMANDS["get active stations in BAND"].replace("BAND", BANDS[band])
    registered_stations = ssh.send_command(cmd=cmd, method= False).split("\n")

    for station in registered_stations:
        if "Active=1" in station:
            # Get station index
            station_idx = int(station.split("AssociatedDevice.")[1].split(".")[0])
            # Retrieve station data
            cmd_station_info = COMMANDS["get station data"].replace("BAND", BANDS[band]).replace("INDEX", str(station_idx))
            station_data = ssh.send_command(cmd=cmd_station_info, method= False).split("\n")
            # Create station dict
            station_dict = {}
            _separator = f"AssociatedDevice.{station_idx}."
            for line in station_data:
                if line.endswith(_separator) or "=" not in line:
                    continue
                field = line.split(f"AssociatedDevice.{station_idx}.")[1]
                key, value = field.split("=")
                key = key.split(".")[-1]
                station_dict[key] = value
            # Append to active stations list
            active_stations.append(station_dict)
    # Return active stations
    return active_stations


def get_connected_stations(ssh: SshClient):
    """Retrive the list of mac addresses of the stations connected to each frequency band"""
    # Get connected stations
    connected_stations_5GHz = []
    connected_stations_2_4GHz = get_connected_stations_in_band(ssh, "2.4GHz")
    # check if 5GHz band is up
    if band_is_up(ssh, "5GHz"):
        connected_stations_5GHz = get_connected_stations_in_band(ssh, "5GHz")
    total_connections = len(connected_stations_2_4GHz) + len(connected_stations_5GHz)

    return total_connections, connected_stations_2_4GHz, connected_stations_5GHz


def band_is_up(ssh: SshClient, band: str):
    """Check if a frequency band is up or down"""
    # Input check
    if band not in BANDS:
        return False

    cmd = COMMANDS["check if band is up"].replace("RADIO", RADIO[band])
    raw_status = ssh.send_command(cmd=cmd, method= False)[1:-1]
    band_status = False if raw_status == "Down" else True
    return band_status


def run_info_connected_stations(
    ssh: SshClient,
    results_dir: str,
    analysis_duration_in_minutes: int,
    sampling_period_in_seconds: int,
    columns_config_file: str
):
    """Entry point for info connected stations program"""

    logger.info("RUNNING PROGRAM: stations info")

    start = datetime.now()
    estimated_end = start + timedelta(minutes=analysis_duration_in_minutes)
    logger.info(f"Estimated end: {str(estimated_end)}")

    # Create connected stations results file
    results_file_path = f"{results_dir}/{RESULTS_FILE_CONNECTIONS_NUMBER}"

    try:
        with open(results_file_path, 'x') as file:
            # Write header
            header = "connected    2.4GHz    5GHz    datetime\n"
            file.write(header)
            logger.info(f"{results_file_path} results file created")
    except FileExistsError:
        logger.error(f"The file '{results_file_path}' already exists.")


    # Waiting loop
    now = datetime.now()
    while now < estimated_end:
        next_sample_at = now + timedelta(seconds=sampling_period_in_seconds)

        # Get number of connected stations
        total_connections, connected_stations_2_4GHz, connected_stations_5GHz = get_connected_stations(ssh)
        logger.info(
            f"Connected stations: {total_connections} 2.4GHz band: {len(connected_stations_2_4GHz)} 5GHz band: {len(connected_stations_5GHz)}")

        # Write number of connections in dedicated file
        write_nb_connections_in_file(
            ssh=ssh,
            results_file=results_file_path,
            connections_number=total_connections,
            connections_2_4GHz=len(connected_stations_2_4GHz),
            connections_5GHz=len(connected_stations_5GHz),
        )
        if total_connections > 0:
            write_stations_info_in_file(
                ssh=ssh,
                results_dir=results_dir,
                connections_2_4GHz=connected_stations_2_4GHz,
                connections_5GHz=connected_stations_5GHz,
                columns_conf=columns_config_file,
            )
        now = datetime.now()

        while now < next_sample_at:
            time.sleep(0.1)
            now = datetime.now()
