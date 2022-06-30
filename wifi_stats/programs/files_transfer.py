""" Objectif      : Envoyer des fichiers en continu aux stations connectées, afin de créer du trafic dans le réseau. Ce trafic permettra de rendre les données récupérées
                   sur les bandes de fréquences  plus interressante
    Comment       : On récupère les adresses IP connectés sur le réseau, puis on envoie un fichier aléatoire (dans notre liste des fichiers) avec un débit aléatoire
                   (entre 1 et 400 000) à chaque adresse IP. Cette action est placé dans un LoopTimer et s'arrete lorsque la durée paramétrer en amont arrive à sa fin
    Données récupérées: la ligne d'envoi du fichier avec toutes ces caractéristiques: horodatage, nom du fichier envoyé, adresse IP de la station, débit utilisé
    Flexibilité   : Durant l'exécution de ce programme, les stations ayant déja été connectée au début pourront se déconnecter et se reconnecté
    Inconvéniants : -Le nombres de stations connectées au Wi-Fi seront au maximum de 3.
                    -De plus, de nouvelles stations ne s'étant pas connectées au début du test, ne pourront pas se connecter pendant le test
"""

# Importation des librairies
from datetime import datetime, timedelta
from time import sleep
import random
from random import randint
from threading import Thread, Event
import os
import re
import subprocess
from typing import Dict
import yaml

import re
from datetime import datetime
import logging
import time
from common.telnet import Telnet

logger = logging.getLogger(__name__)
# TODO: LOGS

LIVEBOX_IP_ADDRESS = "192.168.1.1"

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
        occurenc_max = duration / interval
        logger.info(f"Files to send: {occurenc_max}")
        return occurenc_max

    def cancel(self):
        """Stop the timer if it hasn't finished yet."""
        self.finished.set()

    def run(self):
        if self.wait_first_time:
            self.finished.wait(self.interval)
            self.wait_first_time = True
        # Increment curr_occurences if curr_occ < max_occ
        if not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
            self.curr_occurrences += 1
        # Loops stops after max_occurrences
        if (
            self.curr_occurrences >= self.max_occurrences
        ):
            self.finished.set()
        else:
            # Run timer
            self.run()


def get_random_data_rate():
    """sélectionne un débit au hasard dans la liste des débits. La retourne comme second argument dans la fonction envoie_script"""
    return str(
        randint(1, 400000)
    )  # en kbps # la valeur retourné correspond au seuil max du débit utilisé lors du téléchargement d'un fichier


def select_random_file(files_path: str):
    # sélectionne un fichier au hasard dans la liste des dfichiers. La retourne comme deuxième argument dans la fonction envoie_script
    files_list = os.listdir(files_path)
    selected_file = f"{files_path}{random.choice(files_list)}"
    return selected_file


def send_file_to_station(station, files_path: str):

    # Get station params
    station_ip = station["ip"]
    ssh_usr = station["ssh_user"]
    ssh_password = station["ssh_password"]
    # Get transfer params
    data_rate = get_random_data_rate()
    _file = select_random_file(files_path)

    # Log start of transfer
    _log_line = f"Seding file {_file} to {station_ip} rate: {data_rate} kbps "
    logger.info(_log_line)


    # Run SCP file transfer
    scp_command = (
        f"sshpass -p '{ssh_password}' scp -l {data_rate} {_file} {ssh_usr}@{station_ip}:Documents"
    )
    os.system(scp_command)
    sleep(0.2)  # TODO: NECSSARY ?


def get_test_params(config_file: str):
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


def run_files_transfer(config_file: str, duration_in_minutes: int):
    logger.info("RUNNING PROGRAM: files transfer")
    start = datetime.now()
    estimated_end = start + timedelta(minutes=duration_in_minutes)
    logger.info(f"Estimated end: {str(estimated_end)}")

    stations_dict, files_path = get_test_params(config_file=config_file)

    file_senders  = []

    for station in stations_dict:
        file_sender = FilesSender(
            interval=station["send_interval"],
            duration=duration_in_minutes,
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

    # Kill threads
    for file_sender in file_senders:
        file_sender.finished.set()
    return
