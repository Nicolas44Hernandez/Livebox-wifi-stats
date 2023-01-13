"""
Send files continuously to stations in order to create traffic in the network.
"""

# Importation des librairies
from datetime import datetime, timedelta
from time import sleep
import random
from random import randint
from threading import Thread, Event
import os
from typing import Dict
import yaml
from datetime import datetime
import logging
import time

logger = logging.getLogger(__name__)

class FilesSender(Thread):
    def __init__(
        self, interval, duration, function, args=None, kwargs=None, wait_first_time=True
    ):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.wait_first_time = wait_first_time
        self.max_occurrences = self.__get_occurrences(interval, duration)
        self.curr_occurrences = 0
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.finished = Event()

    def __get_occurrences(self, interval, duration):
        """Returns the number of times that the file will be sent"""
        occurenc_max = (duration * 60) / interval
        logger.info(f"Files to send: {occurenc_max}")
        return occurenc_max

    def cancel(self):
        """Stop the timer if it hasn't finished yet."""
        self.finished.set()

    def run(self):
        """Starts the file transfer"""
        if self.wait_first_time:
            self.finished.wait(self.interval)
            self.wait_first_time = True
        self.kwargs["transfer_number"] = self.curr_occurrences -1
        if not self.finished.is_set():
            logger.info(f"Iteration: {self.curr_occurrences}")
            if self.curr_occurrences <= self.args[0]["transfer_nb_per_step"]:
                time.sleep(20)
            else:
                self.function(*self.args, **self.kwargs)
            self.curr_occurrences += 1
        # Loops stops after max_occurrences
        if (
            self.curr_occurrences >= self.max_occurrences
        ):
            logger.info(f"finished setted")
            self.finished.set()
        else:
            # Run timer
            self.run()

def select_random_file(files_path: str):
    """select a random file from the list."""

    files_list = os.listdir(files_path)
    selected_file = f"{files_path}{random.choice(files_list)}"
    return selected_file

def get_iteration_file(files_path:str, iteration: int, transfers_per_step: int):
    """Get file for iteration"""
    file_numner = int(iteration / transfers_per_step)
    selected_file = f"{files_path}random_file{file_numner}.txt"
    return selected_file


def send_file_to_station(station, files_path: str, transfer_number: int):
    """Send a ramdom file with a random rate to a station over SCP"""

    # Get station params
    station_ip = station["ip"]
    ssh_usr = station["ssh_user"]
    ssh_password = station["ssh_password"]
    throughput_increment = station["throughput_increment_in_kbps"]
    transfer_nb_per_step = station["transfer_nb_per_step"]
    initial_data_rate = station["initial_data_rate_in_kbps"]
    if throughput_increment is None:
        data_rate = initial_data_rate
        _file = select_random_file(files_path)
    else:
        data_rate = initial_data_rate + (throughput_increment * int(transfer_number / transfer_nb_per_step))
        _file = get_iteration_file(files_path,transfer_number, transfer_nb_per_step)

    # Log start of transfer
    _log_line = f"Sending file {_file} to {station_ip} rate: {data_rate} kbps "
    logger.info(_log_line)

    # Run SCP file transfer
    scp_command = (
        f"sshpass -p '{ssh_password}' scp -l {data_rate} {_file} {ssh_usr}@{station_ip}:files_transfer/file.txt"
    )
    os.system(scp_command)
    # sleep(0.2)
    logger.info("File sent")
    # scp_command_rm = (
    #     f"sshpass -p '{ssh_password}' ssh {ssh_usr}@{station_ip} rm -r /home/{ssh_usr}/files_transfer/*"
    # )
    # os.system(scp_command_rm)
    # sleep(0.2)
    # logger.info("File removed")


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


def run_files_transfer(config_file: str, analysis_duration_in_minutes: int):
    """Entry point for files transfer program"""

    logger.info("RUNNING PROGRAM: files transfer")
    start = datetime.now()
    estimated_end = start + timedelta(minutes=analysis_duration_in_minutes)
    logger.info(f"Estimated end: {str(estimated_end)}")

    stations_dict, files_path = get_test_params(config_file=config_file)

    file_senders  = []

    for station in stations_dict:
        file_sender = FilesSender(
            interval=station["send_interval_in_secs"],
            duration=analysis_duration_in_minutes,
            function=send_file_to_station,
            args=(station, files_path),
        )
        file_sender.start()
        file_senders.append(file_sender)

    # Waiting loop
    now = datetime.now()
    while now < estimated_end:
        time.sleep(60)
        now = datetime.now()

    logger.info(f"script END, killing active threads")
    # Kill threads
    for file_sender in file_senders:
        file_sender.finished.set()
    return
