"""
Calibrate smoth rssi for the analysis
"""

from datetime import datetime, timedelta
import logging
import time
from common.ssh import SshClient
from wifi_stats.programs.stations_stats import get_connected_stations

logger = logging.getLogger(__name__)


COMMANDS = {
    "get station MAC": "WiFi.AccessPoint.BAND.AssociatedDevice.INDEX.MACAddress",
    "get station single field": "WiFi.AccessPoint.BAND.AssociatedDevice.INDEX.FIELD",
}
BANDS = {"2.4GHz":"2", "5GHz": "1"}

VALUES_TO_CALIBRATE = ["SignalStrength", "MACAddress"]


def run_calibrate_station(
    ssh: SshClient,
    station_mac: str,
):
    """Entry point for initial calibrate stations program"""

    logger.info(
        f"RUNNING PROGRAM: initial calibrate station MAC: {station_mac}")

    now = datetime.now()

    while True:
        next_sample_at = now + timedelta(seconds=1)

        # Get number of connected stations
        total_connections, connected_stations_2_4GHz, connected_stations_5GHz = get_connected_stations(ssh=ssh)
        connected_stations = connected_stations_2_4GHz + connected_stations_5GHz

        # Check if requested station is connected
        _connected = False
        station_to_calibrate = None
        for station in connected_stations:
            if station["MACAddress"].replace("\"", "") == station_mac:
                _connected = True
                station_to_calibrate = station
                break
        # If the station isn't connected
        if not _connected:
            logger.error(f"The station {station_mac} is not connected")

        else:
            for field in VALUES_TO_CALIBRATE:
                if field not in station_to_calibrate:
                    logger.info(f"{field} is not present in station data")
                    continue
                logger.info(f"{field}: {station_to_calibrate[field]}")

        now = datetime.now()

        while now < next_sample_at:
            time.sleep(0.1)
            now = datetime.now()
