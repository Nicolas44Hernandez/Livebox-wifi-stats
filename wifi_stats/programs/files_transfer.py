"""
Send files continuously to stations in order to create traffic in the network.
"""

from datetime import datetime, timedelta
from threading import Thread, Event
import os
import pexpect
import subprocess
from typing import Iterable
import yaml
from datetime import datetime
import logging
import time

logger = logging.getLogger(__name__)


class FilesTransferManager(Thread):
    def __init__(
        self,
        throughputs: Iterable[int],
        files_path: str,
        function: callable,
        interval_duration_secs: int = 10,
        args=None,
        kwargs=None,
    ):
        Thread.__init__(self)
        self.throughputs = throughputs
        self.files_path = files_path
        self.function = function
        self.interval_duration_secs = interval_duration_secs
        self.max_occurrences = len(throughputs) - 1
        self.curr_occurrences = 0
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.finished = Event()

    def cancel(self):
        """Stop the timer if it hasn't finished yet."""
        self.finished.set()

    def run(self):
        """Starts the file transfer"""
        self.kwargs["transfer_number"] = self.curr_occurrences
        self.kwargs["transfer_direction"] = self.throughputs[self.curr_occurrences]["direction"]
        self.kwargs["throughput"] = self.throughputs[self.curr_occurrences]["throughput_Mbs"]
        self.kwargs["interval_duration"] = self.interval_duration_secs
        if not self.finished.is_set():
            if self.curr_occurrences == 0:
                logger.info(
                    f"Initial deadtime: {self.interval_duration_secs} secs")
                time.sleep(self.interval_duration_secs)
            self.function(*self.args, **self.kwargs)
            self.curr_occurrences += 1
        # Loops stops after max_occurrences
        if (
            self.curr_occurrences > self.max_occurrences
        ):
            logger.info(f"finished setted")
            self.finished.set()
        else:
            # Run timer
            self.run()


def get_iteration_file(files_path: str):
    """Get file for iteration"""
    selected_file = f"{files_path}random_file.txt"
    return selected_file

def transfer_file_scp(
    _file: str,
    data_rate_kbps: int,
    station,
    transfer_max_duration: int,
    transfer_direction: str,
):
    """Transfer file from/to station via SCP protocol"""
    station_ip = station["ip"]
    station_name = station["name"]
    ssh_usr = station["ssh_user"]
    ssh_password = station["ssh_password"]
    transfer_protocol = station["protocol"]
    operative_system = station["operative_system"]

    transfer_from_station = True if transfer_direction == "uplink" else False

    # Log transfert
    f = _file.split("/")[-1]
    _ll = f"Retreiving file {f} from" if transfer_from_station else f"Sending file {f} to"
    _log_line = f"{_ll} {station_ip} rate:{data_rate_kbps} kbps protocol:{transfer_protocol}  os:{operative_system}"
    logger.info(_log_line)

    # Generate transfert scp command
    if transfer_from_station:
        file_to_get = _file.split("/")[-2] + "/" + _file.split("/")[-1]
        command = (
            f"sshpass -p '{ssh_password}' scp -l {data_rate_kbps} {ssh_usr}@{station_ip}:files_transfer/{file_to_get} file_{station_name}.txt"
        )
    else:
        command = (
            f"sshpass -p '{ssh_password}' scp -l {data_rate_kbps} {_file} {ssh_usr}@{station_ip}:files_transfer/file.txt"
        )
    # Log generated command
    logger.info(f"command: {command}")

    # Execute command
    try:
        subprocess.call(command, shell=True, timeout=transfer_max_duration)
    except subprocess.TimeoutExpired:
        logger.info("Transfert end timer")
    else:
        logger.info("Transfert completed")
    return True


def transfer_file_sftp(
    _file: str,
    data_rate_kbps: int,
    station,
    transfer_max_duration: int,
    transfer_direction: str,
):
    """Transfer file from/to station via SFTP protocol"""

    station_ip = station["ip"]
    station_name = station["name"]
    port = station["port"]
    ssh_usr = station["ssh_user"]
    ssh_password = station["ssh_password"]
    transfer_protocol = station["protocol"]
    connection_time = station["connection_time"]
    operative_system = station["operative_system"]

    # Get start transfer timestamp
    _start = datetime.now()

    # Create sftp connection
    cmd_connect = (
        f"sshpass -p '{ssh_password}' sftp -P {port} -l {data_rate_kbps} -oHostKeyAlgorithms=+ssh-rsa {ssh_usr}@{station_ip}:/files/"
    )
    try:
        logger.info("connection start")
        child = pexpect.spawn(cmd_connect)
        child.expect("sftp> ", timeout=connection_time)
        logger.info("Connected")
    except Exception as e:
        logger.error("Error in connection")
        child.close()
        return False

    # Get end connection timestamp
    _end = datetime.now()

    # Get remaining time for transfert
    _delta = (_end - _start).total_seconds()
    remaining_time_for_transfert = transfer_max_duration - _delta
    logger.info(f"Remaining time for transfert: {remaining_time_for_transfert}")

    transfer_from_station = True if transfer_direction == "uplink" else False

    # Log transfert
    file_to_get = _file.split("/")[-2] + "/" + _file.split("/")[-1]
    _ll = f"Retreiving file {file_to_get} from " if transfer_from_station else f"Sending file {_file} to"
    _log_line = f"{_ll} {station_ip} rate:{data_rate_kbps} kbps protocol:{transfer_protocol}  os:{operative_system}"
    logger.info(_log_line)

    # Verify that file exists
    if not transfer_from_station and not os.path.exists(_file):
        logger.error(
            f"Impossible to send file {_file}. File doesnt exist")
        return False

    # Transfer file from/to station
    cmd = f"get {file_to_get} file_{station_name}.txt" if transfer_from_station else f"put {_file} file.txt"
    try:
        # Send command
        child.sendline(cmd)
        child.expect("sftp> ", timeout=remaining_time_for_transfert)
        # Close connection
        child.sendline("exit")
        child.close()
    except Exception:
        logger.info("Transfert end timer")
    else:
        logger.info("Transfert completed")
    return True

def transfer_file(
    station,
    files_path: str,
    transfer_number: int,
    transfer_direction: str,
    throughput: int,
    interval_duration: int,
):
    """Send a ramdom file with a random rate to a station over SCP or SFTP"""
    # If throughput is 0 just wait
    logger.info(
        f"transfer_number: {transfer_number}, throughput: {throughput} Mbps  transfer_duration: {interval_duration}")
    if throughput == 0:
        time.sleep(interval_duration)
        return

    # Get station params
    transfer_protocol = station["protocol"]
    transfer_from_station = True if transfer_direction == "uplink" else False

    # Get transfert params
    data_rate_kbps = int(throughput * 1000)
    _file = get_iteration_file(files_path)

    # Log start of transfer
    logger.info(f"Iteration: {transfer_number}")

    if transfer_protocol == "scp":
        # SCTP file transfer
        transfer_file_scp(
            _file=_file,
            data_rate_kbps=data_rate_kbps,
            station=station,
            transfer_max_duration=interval_duration,
            transfer_direction=transfer_direction,
        )

    elif transfer_protocol == "sftp":
        # SCTP file transfer
        transfer_file_sftp(
                _file=_file,
                data_rate_kbps=data_rate_kbps,
                station=station,
                transfer_max_duration=interval_duration,
                transfer_direction=transfer_direction,
            )
    logger.info("Iteration done")


def get_test_params(config_file: str):
    """
    Retrieve the following test params from the yml config file:
    - STATIONS: stations where the files are going to be send and scp config
    - FILES_PATH: files to send folder in master station
    """

    logger.info(f"Config file: {config_file}")
    # Read yml config file
    with open(config_file, "r") as stream:
        try:
            parsed_yaml = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error(exc)

    # Extract data
    stations_dict = parsed_yaml["STATIONS"]
    files_path = parsed_yaml["FILES_PATH"]

    return stations_dict, files_path


def get_throughputs_dict_from_file(traffic_config_file: str):
    """
    Retrieve the throughput dict from the yml config file
    """

    logger.info(f"Trafic config file: {traffic_config_file}")
    # Read yml config file
    with open(traffic_config_file, "r") as stream:
        try:
            parsed_yaml = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error(exc)

    # Extract data
    return parsed_yaml


def run_files_transfer(
    stations_config: str,
    traffic_config_file: str,
    analysis_duration_in_minutes: int,
    transfert_duration_in_secs: int
):
    """Entry point for files transfer program"""

    logger.info("RUNNING PROGRAM: files transfer")
    start = datetime.now()
    estimated_end = start + timedelta(minutes=analysis_duration_in_minutes)
    logger.info(f"Estimated end: {str(estimated_end)}")

    stations_dict, files_path = get_test_params(config_file=stations_config)
    throughputs_dict = get_throughputs_dict_from_file(
        traffic_config_file=traffic_config_file)

    file_transfer_workers = []

    for station in stations_dict:
        station_name = station["name"]
        throughputs = throughputs_dict[station_name]

        file_transfer_worker = FilesTransferManager(
            throughputs=throughputs,
            files_path=files_path,
            function=transfer_file,
            interval_duration_secs=transfert_duration_in_secs,
            args=(station, files_path)
        )

        file_transfer_worker.start()
        file_transfer_workers.append(file_transfer_worker)

    # Waiting loop
    now = datetime.now()
    while now < estimated_end:
        time.sleep(60)
        now = datetime.now()

    logger.info(f"script END, killing active threads")
    # Kill threads
    for file_worker in file_transfer_workers:
        file_worker.finished.set()
    return
