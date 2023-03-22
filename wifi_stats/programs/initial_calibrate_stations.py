"""
Calibrate smoth rssi for the analysis
"""

from datetime import datetime, timedelta
import logging
import time
from common.telnet import Telnet
import yaml
from programs.info_connected_stations import get_connected_stations, parse_telnet_output


logger = logging.getLogger(__name__)


COMMANDS = {
    "get station info": "echo -n 'EE''EE '; wl -i BAND sta_info MAC_ADDRESS; echo 'FF''FF'",
}

VALUES_TO_CALIBRATE = ["smoothed rssi"]


def run_calibrate_station(
    telnet: Telnet,
    station_mac: str,
):
    """Entry point for initial calibrate stations program"""

    logger.info(
        f"RUNNING PROGRAM: initial calibrate station MAC: {station_mac}")

    now = datetime.now()

    while True:
        next_sample_at = now + timedelta(seconds=1)

        # Get number of connected stations
        total_connections, connected_stations_2_4GHz, connected_stations_5GHz = get_connected_stations(
            telnet)

        connected_stations = connected_stations_2_4GHz + connected_stations_5GHz
        if total_connections > 0:
            # Check if station to calibrate is connected
            if station_mac in connected_stations:
                connected_to_band = "5GHz" if station_mac in connected_stations_5GHz else "2.4GHz"
                # retrieve station info
                sta_info_command = COMMANDS["get station info"].replace(
                    "MAC_ADDRESS", station_mac)
                if connected_to_band == "5GHz":
                    sta_info_command = sta_info_command.replace("BAND", "wl0")
                elif connected_to_band == "2.4GHz":
                    sta_info_command = sta_info_command.replace("BAND", "wl2")
                else:
                    sta_info_command = sta_info_command.replace("BAND", "wl1")
                station_info_result_brut = telnet.send_command_and_read_result(
                    sta_info_command)
                _raw_station_info = str(parse_telnet_output(
                    station_info_result_brut)).split("\r\n")[1:-1]

                # create entry
                for key in VALUES_TO_CALIBRATE:
                    for line in _raw_station_info:
                        if key in line:
                            value = line.split(key)[1][1:].replace("= ", "")
                            logger.info(f"{key}: {value}")
            else:
                logger.error(f"The station {station_mac} is not connected")
        else:
            logger.error(f"The station {station_mac} is not connected")

        now = datetime.now()

        while now < next_sample_at:
            time.sleep(0.1)
            now = datetime.now()
