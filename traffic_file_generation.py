
from datetime import datetime
import argparse
import os

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


def generate_requested_throughput_result_file(directory: str, root: str):
    """Generate requested throughputs result file"""

    #directory = "C3_C04-24_SC1"
    _file = f"{root}/{directory}/{FILE_NAME}"

    file1 = open(_file, 'r')
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

    _result_file = f"{root}/{directory}/{RESULT_FILE_NAME}"
    write_result_file(entries_to_write=entries_to_write, result_file=_result_file)

def main():
    """
    Entry point, this method parses the args and run the program
    Args:
        -fd   --files_dir     Directory where the files are
    """
    parser = argparse.ArgumentParser(prog="WiFi-stats")

    parser.add_argument(
        "-fd",
        "--files_dir",
        type=str,
        help="Directory where the files are",
    )

    # Parse args
    args = parser.parse_args()
    directories_list = os.listdir(args.files_dir)

    for directory in directories_list:
        generate_requested_throughput_result_file(directory=directory, root=args.files_dir)

if __name__ == "__main__":
    main()
