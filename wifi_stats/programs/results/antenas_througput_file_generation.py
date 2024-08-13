
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

class ThroughputEntry():
    band: str
    txbytes: int
    rxbytes: int
    timestamp: datetime

    def __init__(self, band: str, txbytes: int, rxbytes: int, timestamp_str: str):
        """Constructor for ThroughputEntry """
        self.band=band
        self.txbytes=txbytes
        self.rxbytes=rxbytes
        self.timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

    def retrieve_line_info(line: str):
        """Returns a ThroughputEntry object from line"""

        band = line.split("BAND:")[-1].split()[0]
        txbyte = line.split("txbyte:")[-1].split()[0]
        rxbyte = line.split("rxbyte:")[-1].split()[0]
        timestamp_str = line.split(" [Thread")[0].split(",")[0]

        return ThroughputEntry(
            band=band,
            txbytes=txbyte,
            rxbytes=rxbyte,
            timestamp_str=timestamp_str
        )

def write_result_file(entries_to_write, result_file:str):
    """Write output file"""
    logger.info(f"Writting result file in {result_file}")
    _file = result_file
    f = open(_file, "w")
    f.write(f"BAND\tRXBYTES\tTXBYTES\tTIMESTAMP\n")
    for entry in entries_to_write:
        f.write(f"{entry.band}\t{entry.rxbytes}\t{entry.txbytes}\t{entry.timestamp}\n")
    f.close()


def generate_antenas_real_throughput_result_file(log_file: str, result_file: str):
    """Generate antenas real throughputs result file"""
    logger.info("RUNNING PROGRAM: Generate antenas real througput result file")

    # Check if logfile exists
    if not os.path.exists(log_file) or not os.path.isfile(log_file):
        logger.error("Log file doesnt exist, check path")
        return

    # Log config files
    logger.info(f"Antenas stats Log file: {log_file}")

    file1 = open(log_file, 'r')
    Lines = file1.readlines()

    lines_to_use = []
    for line in Lines:
        patterns = ["BAND:"]
        for pattern in patterns:
            if pattern in line:
                lines_to_use.append(line)
                break

    entries_to_write = []
    for line in lines_to_use:
            throughout_entry = ThroughputEntry.retrieve_line_info(line)
            entries_to_write.append(throughout_entry)

    write_result_file(entries_to_write=entries_to_write, result_file=result_file)
