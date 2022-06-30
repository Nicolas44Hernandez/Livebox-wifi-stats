"""Objectif : Récupérées des données non variables : versions, systéme d'exploitation, espace disponible
   Comment  : On se connecte en Telnet pour récupérer certaines données (version des commandes Broadcom) et on se déconnecte pour récupérer les autres
"""

import subprocess
import logging
from common.telnet import Telnet

logger = logging.getLogger(__name__)

STATIC_DATA_FILE =  "static_data.txt"
SEPARATOR = "\n---------------------------------------------------\n"

def write_master_station_infos(telnet: Telnet, results_dir:str):
   # Write master station header
   master_station_header = SEPARATOR + "MASTER STATION INFOS"
   write_master_station_header_command = "echo '" + master_station_header + "' >> " + results_dir + "/" + STATIC_DATA_FILE
   telnet.send_command(write_master_station_header_command)

   # Write master station os
   master_station_os = subprocess.check_output("hostnamectl", shell=True).decode('ascii').strip()
   master_station_os = SEPARATOR + master_station_os
   write_master_station_os_command = "echo '" + master_station_os + "' >> " + results_dir + "/" + STATIC_DATA_FILE
   telnet.send_command(write_master_station_os_command)

   # Write master station python version
   python_version = subprocess.check_output("python3 --version", shell=True).decode('ascii').strip()
   write_python_version_command = "echo 'python version: " + python_version + "' >> " + results_dir + "/" + STATIC_DATA_FILE
   telnet.send_command(write_python_version_command)

   # Write separator
   write_separator_command = "echo '" + SEPARATOR + "' >> " + results_dir + "/" + STATIC_DATA_FILE
   telnet.send_command(write_separator_command)

   print(telnet.connection.read_very_eager().decode('ascii'))

def write_livebox_infos(telnet: Telnet, results_dir:str):
   # Write livebox header
   livebox_header = SEPARATOR + "LIVEBOX INFOS"
   write_livebox_header_command = "echo '" + livebox_header + "' >> " + results_dir + "/" + STATIC_DATA_FILE
   telnet.send_command(write_livebox_header_command)

   # Write livebox name
   _splited_dir = results_dir.split("/")
   livebox_name = _splited_dir[len(_splited_dir) - 2]
   write_livebox_name_command = "echo 'livebox name: " + livebox_name + "' >> " + results_dir + "/" + STATIC_DATA_FILE
   telnet.send_command(write_livebox_name_command)

   # Write Broadcom version
   write_broadcom_version_command = "wl ver" + " >> " + results_dir + "/" + STATIC_DATA_FILE
   telnet.send_command(write_broadcom_version_command)

def run_static_data(telnet: Telnet, results_dir:str, duration_in_minutes: int):
   logger.info("RUNNING PROGRAM: static data")

   # write master stations infos
   write_master_station_infos(telnet, results_dir)

   # write livebox infos
   write_livebox_infos(telnet, results_dir)



