
from datetime import datetime
from logging.config import dictConfig
import logging
import argparse
import os
import yaml

logger = logging.getLogger(__name__)


FILE_NAME="files_transfer.log"
RESULT_FILE_NAME="requested_throughput.txt"
STATIONS = {
    "192.168.1.26": {
        "name": "GALAXY",
        "mac":"6C:C7:EC:2B:2E:D7",
        "mac_":"6C_C7_EC_2B_2E_D7",
    },
    "192.168.1.22": {
        "name": "PCW_01",
        "mac":"78:AF:08:31:B1:18",
        "mac_":"78_AF_08_31_B1_18",
    },
    "192.168.1.25": {
        "name": "RPI_01",
        "mac":"E4:5F:01:E8:C1:2E",
        "mac_":"E4_5F_01_E8_C1_2E",
    },
}

class TransferStart():
    station_name: str
    direction: str
    station_ip: str
    station_mac: str
    station_mac_: str
    throughput_Mbps: int
    protocol: str
    timestamp: datetime

    def __init__(self, direction: str, station_ip: str, throughput_kbps: int, protocol: str, timestamp_str: str):
        """Constructor for TransferStart """
        self.direction=direction
        self.station_ip=station_ip
        self.station_mac=STATIONS[station_ip]["mac"]
        self.station_mac_=STATIONS[station_ip]["mac_"]
        self.station_name=STATIONS[station_ip]["name"]
        self.throughput_Mbps=throughput_kbps/1000
        self.protocol=protocol
        self.timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

    def retrieve_line_info(line: str):
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

        return TransferStart(
            direction=direction,
            station_ip=station_ip,
            throughput_kbps=throughput_kbps,
            protocol=protocol,
            timestamp_str=timestamp_str
        )


class TransferStop():

    station_name: str
    direction: str
    station_ip: str
    station_mac: str
    station_mac_: str
    throughput_Mbps: int
    protocol: str
    timestamp: datetime

    def __init__(self, direction: str, station_ip: str, throughput_Mbps: int, protocol: str, timestamp_str: str):
        """Constructor for TransferStop """
        self.direction=direction
        self.station_ip=station_ip
        self.station_mac=STATIONS[station_ip]["mac"]
        self.station_mac_=STATIONS[station_ip]["mac_"]
        self.station_name=STATIONS[station_ip]["name"]
        self.throughput_Mbps=throughput_Mbps
        self.protocol=protocol
        self.timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

    def get_line_timestamp(line: str):
        """Returns a datetime_str object from line"""
        pattern = " [Thread"
        return line.split(pattern)[0].split(",")[0]

def write_result_file(entries_to_write, result_file:str):
    """Write output file"""
    _file = result_file
    f = open(_file, "w")
    f.write(f"NAME\tSTATION_MAC\tSTATION_MAC_\tIP\tTHROUGHPUT(Mbps)\tPROTOCOL\tUL/DL\tSTATUS\tTIMESTAMP\n")
    for entry in entries_to_write:
        status = "START" if type(entry) is TransferStart else "STOP"
        f.write(f"{entry.station_name}\t{entry.station_mac}\t{entry.station_mac_}\t{entry.station_ip}\t{entry.throughput_Mbps}\t{entry.protocol}\t{entry.direction}\t{status}\t{entry.timestamp}\n")
    f.close()


def generate_requested_throughput_result_file(log_file: str, result_file: str):
    """Generate requested throughputs result file"""

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
                    transfer_in_progress_th1 = TransferStart.retrieve_line_info(line)
                    entries_to_write.append(transfer_in_progress_th1)
                else:
                    if transfer_in_progress_th1 is not None:
                        transfer_stop = TransferStop(
                                direction=transfer_in_progress_th1.direction,
                                station_ip=transfer_in_progress_th1.station_ip,
                                throughput_Mbps=transfer_in_progress_th1.throughput_Mbps,
                                protocol=transfer_in_progress_th1.protocol,
                                timestamp_str=TransferStop.get_line_timestamp(line)
                            )
                        entries_to_write.append(transfer_stop)
                        transfer_in_progress_th1 = None
            elif "Thread-2" in line:
                if "Iteration done" not in line:
                    transfer_in_progress_th2 = TransferStart.retrieve_line_info(line)
                    entries_to_write.append(transfer_in_progress_th2)
                else:
                    if transfer_in_progress_th2 is not None:
                        transfer_stop = TransferStop(
                                direction=transfer_in_progress_th2.direction,
                                station_ip=transfer_in_progress_th2.station_ip,
                                throughput_Mbps=transfer_in_progress_th2.throughput_Mbps,
                                protocol=transfer_in_progress_th2.protocol,
                                timestamp_str=TransferStop.get_line_timestamp(line)
                            )
                        entries_to_write.append(transfer_stop)
                        transfer_in_progress_th2 = None
            elif "Thread-3" in line:
                if "Iteration done" not in line:
                    transfer_in_progress_th3 = TransferStart.retrieve_line_info(line)
                    entries_to_write.append(transfer_in_progress_th3)
                else:
                    if transfer_in_progress_th3 is not None:
                        transfer_stop = TransferStop(
                                direction=transfer_in_progress_th3.direction,
                                station_ip=transfer_in_progress_th3.station_ip,
                                throughput_Mbps=transfer_in_progress_th3.throughput_Mbps,
                                protocol=transfer_in_progress_th3.protocol,
                                timestamp_str=TransferStop.get_line_timestamp(line)
                            )
                        entries_to_write.append(transfer_stop)
                        transfer_in_progress_th3 = None

    write_result_file(entries_to_write=entries_to_write, result_file=result_file)

def main():
    """
    Entry point, this method parses the args and run the program
    Args:
        -tf   --transfer_log_file     Transfer log file
        -rf   --result_file           Result generated file
        -lc     --logs_configuration                  Logs configuration

    """
    parser = argparse.ArgumentParser(prog="WiFi-stats")

    parser.add_argument(
        "-tf",
        "--transfer_log_file",
        type=str,
        help="Transfer log file",
    )

    parser.add_argument(
        "-rf",
        "--result_file",
        type=str,
        help="Result generated file",
    )

    parser.add_argument(
        "-lc",
        "--logs_configuration",
        type=str,
        help="Logs config",
    )

    # Parse args
    args = parser.parse_args()

    # Load logging configuration
    with open(args.logs_configuration) as stream:
        dictConfig(yaml.full_load(stream))


    # Check if logfile exists
    if not os.path.exists(args.transfer_log_file) or not os.path.isfile(args.transfer_log_file):
        logger.error("Log file doesnt exist, check path")
        return

    generate_requested_throughput_result_file(log_file=args.transfer_log_file, result_file=args.result_file)

if __name__ == "__main__":
    main()
