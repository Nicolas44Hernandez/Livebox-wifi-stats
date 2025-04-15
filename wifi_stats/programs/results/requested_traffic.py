
from datetime import datetime
import logging
import os
import yaml

logger = logging.getLogger(__name__)

class TransferStart():
    station_name: str
    direction: str
    station: dict
    throughput_Mbps: int
    protocol: str
    timestamp: datetime

    def __init__(self, direction: str, station: dict, throughput_kbps: int, protocol: str, timestamp_str: str):
        """Constructor for TransferStart """
        self.direction=direction
        self.station=station
        self.throughput_Mbps=throughput_kbps/1000
        self.protocol=protocol
        self.timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

    def retrieve_line_info(line: str, stations: dict):
        """Returns a TransfertStart object from line"""
        patterns = {
            "UL": "Sending file",
            "timestamp_str" : " [Thread",
        }
        direction = "UL" if patterns["UL"] in line else "DL"
        if direction == "UL":
            station_ip = line.split(" to")[1].split()[0]
        else:
            station_ip = line.split(" from ")[1].split()[0]

        protocol = line.split("protocol:")[-1].split()[0]
        throughput_kbps = int(line.split("rate:")[-1].split()[0])
        timestamp_str = line.split(patterns["timestamp_str"])[0].split(",")[0]
        station = stations[station_ip]

        return TransferStart(
            direction=direction,
            station=station,
            throughput_kbps=throughput_kbps,
            protocol=protocol,
            timestamp_str=timestamp_str
        )


class TransferStop():

    station_name: str
    direction: str
    station: dict
    throughput_Mbps: int
    protocol: str
    timestamp: datetime

    def __init__(self, direction: str, station: dict, throughput_Mbps: int, protocol: str, timestamp_str: str):
        """Constructor for TransferStop """
        self.direction=direction
        self.station=station
        self.throughput_Mbps=throughput_Mbps
        self.protocol=protocol
        self.timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

    def get_line_timestamp(line: str):
        """Returns a datetime_str object from line"""
        pattern = " [Thread"
        return line.split(pattern)[0].split(",")[0]

def write_result_file(entries_to_write, stations: dict, result_file:str):
    """Write output file"""
    logger.info(f"Writting result file in {result_file}")
    _file = result_file
    f = open(_file, "w")
    f.write(f"NAME\tSTATION_MAC\tSTATION_MAC_\tIP\tTHROUGHPUT(Mbps)\tPROTOCOL\tUL/DL\tSTATUS\tTIMESTAMP\n")
    for entry in entries_to_write:
        status = "START" if type(entry) is TransferStart else "STOP"
        station_name = entry.station["name"]
        station_mac = entry.station["mac"]
        station_mac_ = entry.station["mac_"]
        station_ip = entry.station["ip"]
        f.write(f"{station_name}\t{station_mac}\t{station_mac_}\t{station_ip}\t{entry.throughput_Mbps}\t{entry.protocol}\t{entry.direction}\t{status}\t{entry.timestamp}\n")
    f.close()


def generate_requested_throughput_result_file(log_file: str, result_file: str, stations_config_file: str):
    """Generate requested throughputs result file"""
    logger.info("RUNNING PROGRAM: Generate requested througput result file")

    # Check if logfile exists
    if not os.path.exists(log_file) or not os.path.isfile(log_file):
        logger.error("Log file doesnt exist, check path")
        return

    # Check if stations config file exists
    if not os.path.exists(stations_config_file) or not os.path.isfile(stations_config_file):
        logger.error("Stations config file doesnt exist, check path")
        return

    # Log config files
    logger.info(f"Stations config file: {stations_config_file}")
    logger.info(f"Files transfert Log file: {log_file}")

    # Read yml stations config and retreive stations
    with open(stations_config_file, "r") as stream:
        try:
            parsed_yaml = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error(exc)

    # Extract data
    stations = {}
    for station in parsed_yaml["STATIONS"]:
        stations[station["ip"]] = {
            "name": station["name"],
            "ip": station["ip"],
            "mac": station["mac"],
            "mac_": station["mac"].replace(":", "_")
        }


    file1 = open(log_file, 'r')
    Lines = file1.readlines()

    lines_to_use = []
    for line in Lines:
        patterns = ["Sending file", "Retreiving file", "Iteration done"]
        for pattern in patterns:
            if pattern in line:
                lines_to_use.append(line)
                break

    entries_to_write = []
    transfer_in_progress_th1 = None
    transfer_in_progress_th2 = None
    transfer_in_progress_th3 = None

    for line in lines_to_use:
            if "Thread-1" in line:
                if "Iteration done" not in line:
                    transfer_in_progress_th1 = TransferStart.retrieve_line_info(line, stations)
                    entries_to_write.append(transfer_in_progress_th1)
                else:
                    if transfer_in_progress_th1 is not None:
                        transfer_stop = TransferStop(
                                direction=transfer_in_progress_th1.direction,
                                station=transfer_in_progress_th1.station,
                                throughput_Mbps=transfer_in_progress_th1.throughput_Mbps,
                                protocol=transfer_in_progress_th1.protocol,
                                timestamp_str=TransferStop.get_line_timestamp(line)
                            )
                        entries_to_write.append(transfer_stop)
                        transfer_in_progress_th1 = None
            elif "Thread-2" in line:
                if "Iteration done" not in line:
                    transfer_in_progress_th2 = TransferStart.retrieve_line_info(line, stations)
                    entries_to_write.append(transfer_in_progress_th2)
                else:
                    if transfer_in_progress_th2 is not None:
                        transfer_stop = TransferStop(
                                direction=transfer_in_progress_th2.direction,
                                station=transfer_in_progress_th2.station,
                                throughput_Mbps=transfer_in_progress_th2.throughput_Mbps,
                                protocol=transfer_in_progress_th2.protocol,
                                timestamp_str=TransferStop.get_line_timestamp(line)
                            )
                        entries_to_write.append(transfer_stop)
                        transfer_in_progress_th2 = None
            elif "Thread-3" in line:
                if "Iteration done" not in line:
                    transfer_in_progress_th3 = TransferStart.retrieve_line_info(line, stations)
                    entries_to_write.append(transfer_in_progress_th3)
                else:
                    if transfer_in_progress_th3 is not None:
                        transfer_stop = TransferStop(
                                direction=transfer_in_progress_th3.direction,
                                station=transfer_in_progress_th3.station,
                                throughput_Mbps=transfer_in_progress_th3.throughput_Mbps,
                                protocol=transfer_in_progress_th3.protocol,
                                timestamp_str=TransferStop.get_line_timestamp(line)
                            )
                        entries_to_write.append(transfer_stop)
                        transfer_in_progress_th3 = None

    write_result_file(entries_to_write=entries_to_write, stations=stations, result_file=result_file)
