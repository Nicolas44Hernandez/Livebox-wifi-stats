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
        interval_duration_secs: int = 20,
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
        self.kwargs["times_to_send"] = self.throughputs[self.curr_occurrences]["times"]
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


def get_iteration_file(files_path: str, throughput: int, ):
    """Get file for iteration"""
    selected_file = f"{files_path}random_file_{throughput}MB.txt"
    return selected_file


def send_file_scp(
    _file: str,
    data_rate_kbps: int,
    station, times_to_send: int,
    interval_duration: int,
):
    """Transfer file to station via SCP protocol"""

    station_ip = station["ip"]
    ssh_usr = station["ssh_user"]
    ssh_password = station["ssh_password"]
    transfer_protocol = station["protocol"]
    operative_system = station["operative_system"]
    connection_time = station["connection_time"]

    transfer_duration = interval_duration/times_to_send

    if not os.path.exists(_file):
        logger.error(
            f"Impossible to send file {_file}. File doesnt exist")
        return False

    f = _file.split("/")[-1]
    _log_line = f"Sending file {f} to {station_ip} rate:{data_rate_kbps} kbps times: {times_to_send} protocol:{transfer_protocol} os:{operative_system}"
    logger.info(_log_line)
    command = (
        f"sshpass -p '{ssh_password}' scp -l {data_rate_kbps} {_file} {ssh_usr}@{station_ip}:files_transfer/file.txt"
    )

    for i in range(times_to_send):
        # logger.info(f"command: {command}")
        time.sleep(connection_time)
        try:
            logger.info(f"Tx number {i}")
            subprocess.call(command, shell=True, timeout=transfer_duration)
        except subprocess.TimeoutExpired:
            logger.error("Transfer is taking too long, cancelling transfer")
    return True


def retreive_file_scp(
    _file: str,
    data_rate_kbps: int,
    station, times_to_send: int,
    interval_duration: int
):
    """Transfer file from station via SCP protocol"""

    station_ip = station["ip"]
    station_name = station["name"]
    ssh_usr = station["ssh_user"]
    ssh_password = station["ssh_password"]
    transfer_protocol = station["protocol"]
    operative_system = station["operative_system"]
    connection_time = station["connection_time"]

    transfer_duration = interval_duration/times_to_send

    f = _file.split("/")[-1]
    _log_line = f"Retreiving file {f} from {station_ip} rate:{data_rate_kbps} kbps  times: {times_to_send} protocol:{transfer_protocol}  os:{operative_system}"
    logger.info(_log_line)
    file_to_get = _file.split(
        "/")[-2] + "/" + _file.split("/")[-1]
    command = (
        f"sshpass -p '{ssh_password}' scp -l {data_rate_kbps} {ssh_usr}@{station_ip}:files_transfer/{file_to_get} file_{station_name}.txt"
    )

    for i in range(times_to_send):
        # logger.info(f"command: {command}")
        time.sleep(connection_time)
        try:
            logger.info(f"Rx number {i}")
            subprocess.call(command, shell=True, timeout=transfer_duration)
        except subprocess.TimeoutExpired:
            logger.error("Transfer is taking too long, cancelling transfer")
    return True


def send_file_sftp(
    _file: str,
    data_rate_kbps: int,
    station,
    times_to_send: int,
    interval_duration: int,
):
    """Transfer file to station via SFTP protocol"""

    station_ip = station["ip"]
    port = station["port"]
    ssh_usr = station["ssh_user"]
    ssh_password = station["ssh_password"]
    transfer_protocol = station["protocol"]
    connection_time = station["connection_time"]

    transfer_duration = interval_duration/times_to_send

    cmd_connect = (
        f"sshpass -p '{ssh_password}' sftp -P {port} -l {data_rate_kbps} -oHostKeyAlgorithms=+ssh-rsa {ssh_usr}@{station_ip}:/files/"
    )
    try:
        # Create sftp connection
        logger.info("connection start")
        child = pexpect.spawn(cmd_connect)
        child.expect("sftp> ", timeout=connection_time)
        logger.info("Connected")

        if not os.path.exists(_file):
            logger.error(
                f"Impossible to send file {_file}. File doesnt exist")
            return False
        _log_line = f"Sending file {_file} to {station_ip} rate:{data_rate_kbps} kbps times: {times_to_send} protocol:{transfer_protocol}"
        logger.info(_log_line)

        for i in range(times_to_send):
            try:
                logger.info(f"Tx number {i}")
                cmd = f"put {_file} file.txt"
                child.sendline(cmd)
                child.expect("sftp> ", timeout=transfer_duration)

                # Close connection
                child.sendline("exit")
                child.close()
            except Exception as e:
                logger.error(
                    "Transfer is taking too long, cancelling transfer")
    except Exception as e:
        logger.error("Error in transfer")
        child.close()
        return False
    return True


def retreive_file_sftp(
    _file: str,
    data_rate_kbps: int,
    station,
    times_to_send: int,
    interval_duration: int,
):
    """Transfer file from station via SFTP protocol"""

    station_ip = station["ip"]
    station_name = station["name"]
    port = station["port"]
    ssh_usr = station["ssh_user"]
    ssh_password = station["ssh_password"]
    transfer_protocol = station["protocol"]
    connection_time = station["connection_time"]

    transfer_duration = interval_duration/times_to_send

    cmd_connect = (
        f"sshpass -p '{ssh_password}' sftp -P {port} -l {data_rate_kbps} -oHostKeyAlgorithms=+ssh-rsa {ssh_usr}@{station_ip}:/files/"
    )
    try:
        # Create sftp connection
        logger.info("connection start")
        child = pexpect.spawn(cmd_connect)
        child.expect("sftp> ", timeout=connection_time)
        logger.info("Connected")

        file_to_get = _file.split("/")[-2] + "/" + _file.split("/")[-1]
        _log_line = f"Retreiving file {file_to_get} from {station_ip} rate:{data_rate_kbps} kbps  times: {times_to_send}  protocol:{transfer_protocol}"
        logger.info(_log_line)

        for i in range(times_to_send):
            try:
                logger.info(f"Rx number {i}")
                cmd = f"get {file_to_get} file_{station_name}.txt"
                child.sendline(cmd)
                child.expect("sftp> ", timeout=transfer_duration)

                # Close connection
                child.sendline("exit")
                child.close()
            except Exception as e:
                logger.error(
                    "Transfer is taking too long, cancelling transfer")
    except Exception as e:
        logger.error("Error in transfer")
        child.close()
        return False
    return True


def transfer_file(
    station,
    files_path: str,
    transfer_number: int,
    transfer_direction: str,
    throughput: int,
    interval_duration: int,
    times_to_send: int,
):
    """Send a ramdom file with a random rate to a station over SCP"""
    # If throughput is 0 just wait
    logger.info(
        f"transfer_number: {transfer_number}, throughput: {throughput} Mbps  interval_duration: {interval_duration}")
    if throughput == 0:
        time.sleep(interval_duration)
        return

    # Get station params
    transfer_protocol = station["protocol"]
    transfer_from_station = True if transfer_direction == "uplink" else False

    # Get transfert params
    data_rate_kbps = throughput * 1000
    _file = get_iteration_file(files_path, throughput)

    # Log start of transfer
    logger.info(f"Iteration: {transfer_number}")

    if transfer_protocol == "scp":
        # SCTP file transfer
        if transfer_from_station:
            retreive_file_scp(
                _file=_file,
                data_rate_kbps=data_rate_kbps,
                station=station,
                times_to_send=times_to_send,
                interval_duration=interval_duration,
            )
        else:
            send_file_scp(
                _file=_file,
                data_rate_kbps=data_rate_kbps,
                station=station,
                times_to_send=times_to_send,
                interval_duration=interval_duration,
            )

    elif transfer_protocol == "sftp":
        # SCTP file transfer
        if transfer_from_station:
            retreive_file_sftp(
                _file=_file,
                data_rate_kbps=data_rate_kbps,
                station=station,
                times_to_send=times_to_send,
                interval_duration=interval_duration,
            )
        else:
            send_file_sftp(
                _file=_file,
                data_rate_kbps=data_rate_kbps,
                station=station,
                times_to_send=times_to_send,
                interval_duration=interval_duration,
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
