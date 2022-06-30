"""Objectif : Récupérer les données sur les appareils/stations connectés à la bande de fréquence 2,4 GHz
   Comment  : On se connecte en Telnet à la Livebox et on exécute des commandes (commandes principales : wl -i wl0 assoclist, wl info_sta)
              afin de récuperer ses données
   Données récupérées : Nombre de stations connectés, Informations sur les stations ( adresses MAC, RSSI, total de paquets...)
"""

import re
from datetime import datetime, timedelta
import logging
import time
from common.telnet import Telnet

logger = logging.getLogger(__name__)

RESULTS_FILE_CONNECTIONS_NUMBER =  "connections_number.txt"
# File name will be completed with the station number info_station{i}.txt
RESULTS_FILE_INFO_STATION =  "info_station"

COMMANDS = {
    "check if 5GHz band is up": 'wl -i wl0 bss',
    "check if 2.4GHz band is up": 'wl -i wl2 bss',
    "get number of stations 5GHz": "echo -n 'EE''EE '; wl -i wl0 assoclist | wc -l; echo 'FF''FF'",
    "get number of stations 2.4GHz": "echo -n 'EE''EE '; wl -i wl2 assoclist | wc -l; echo 'FF''FF'"
}

# Time period between each loop stats TODO: add shared parameter
SLEEP_TIME_BETWEEN_LOOPS=1

def write_stations_info_in_file(
    telnet: Telnet,
    results_dir: str,
    connections_2_4GHz: int,
    connections_5GHz: int
    ):
    total_connections = connections_2_4GHz + connections_5GHz
    date_time = str(datetime.now())
    # loop over stations connected to 2.4GHZ band
    for i in range(1, total_connections + 1):
        # redirection to file command
        if i < connections_2_4GHz:
            output_redirection_command = f" >> {results_dir}/{RESULTS_FILE_INFO_STATION}{i}.txt"
            band_alias = "wl2"
        else:
            output_redirection_command = f" >> {results_dir}/{RESULTS_FILE_INFO_STATION}{i+connections_2_4GHz}.txt"
            band_alias = "wl0"

        # Append datetime and band
        station_header_command = f"echo 'datetime: {date_time} \nband: {band_alias}'"
        write_station_header_command = station_header_command + output_redirection_command
        telnet.send_command(write_station_header_command)

        # Append station info
        sta_info_command = "wl -i '"f"'{band_alias} assoclist | sed 's/assoclist //' | sed '"f'{i}'"q;d' | xargs wl sta_info"
        write_stations_info_command = sta_info_command + output_redirection_command
        telnet.send_command(write_stations_info_command)

def write_nb_connections_in_file(telnet: Telnet, results_dir: str, connections_number: int):

    # redirection to file command
    output_redirection_command = " >> " + results_dir + "/" + RESULTS_FILE_CONNECTIONS_NUMBER

    # Write connected stations command
    date_time = str(datetime.now())
    write_connected_stations_command = f"echo stations connectees: {connections_number} --- date: {date_time}" + output_redirection_command

    # Send command
    telnet.send_command(write_connected_stations_command)

def parse_telnet_output(raw_output: str):
    pattern = re.compile(r"EEEE (\d+)")
    for match in pattern.finditer(raw_output):
        return match.group(1)

def get_number_of_connected_stations_in_band(telnet: Telnet, band: str):
    """Returns the number of statiosns connected to the band WiFi"""
    # Input check
    if band not in ["2.4GHz","5GHz"]:
        return 0

    telnet.send_command(COMMANDS["get number of stations " + band]) # # @MAC => # connected stations
    nb_d_addr_result_brut = telnet.connection.read_until(b"FFFF").decode('ascii')
    connected_stations = int(parse_telnet_output(nb_d_addr_result_brut))
    logger.info(f'Stations conected to band %s: %d', band, connected_stations)
    return connected_stations

def get_number_of_connected_stations(telnet: Telnet):
    # Get number of connected stations by band
    connected_stations_5GHz= 0
    connected_stations_2_4GHz= get_number_of_connected_stations_in_band(telnet, "2.4GHz")
    # check if 5GHz band is up
    if band_is_up(telnet, "5GHz"):
        connected_stations_5GHz = get_number_of_connected_stations_in_band(telnet, "5GHz")

    total_connections = connected_stations_2_4GHz + connected_stations_5GHz

    return total_connections, connected_stations_2_4GHz, connected_stations_5GHz

def band_is_up(telnet: Telnet, band: str):
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

def run_info_connected_stations(telnet: Telnet, results_dir:str, duration_in_minutes: int):
    logger.info("RUNNING PROGRAM: stations info")

    start = datetime.now()
    estimated_end = start + timedelta(minutes=duration_in_minutes)
    logger.info(f"Estimated end: {str(estimated_end)}")

    # Waiting loop
    now = datetime.now()
    while now < estimated_end:

        # Get number of connected stations
        total_connections, connected_stations_2_4GHz, connected_stations_5GHz = get_number_of_connected_stations(telnet)
        logger.info(f"Total connected stations: {total_connections}")
        logger.info(f"2.4GHz band connected stations: {connected_stations_2_4GHz}")
        logger.info(f"5GHz band connected stations: {connected_stations_5GHz}")

        # Write number of connections in dedicated file
        write_nb_connections_in_file(
            telnet=telnet,
            results_dir=results_dir,
            connections_number=total_connections
        )
        if total_connections > 0 :
            write_stations_info_in_file(
                telnet=telnet,
                results_dir=results_dir,
                connections_2_4GHz=connected_stations_2_4GHz,
                connections_5GHz=connected_stations_5GHz,
            )
        time.sleep(SLEEP_TIME_BETWEEN_LOOPS)
        now = datetime.now()




