"""
Retrieve static data froml the master station, livebox and connected stations.
"""

import subprocess
import logging
from common import SshClient

logger = logging.getLogger(__name__)

STATIC_DATA_FILE =  "static_data.txt"
SEPARATOR = "\n-----------------------------------------------------------------------------\n"


def append_to_file(file_path: str, line: str) -> bool:
   """Append str to file"""
   try:
      with open(file_path, 'a') as file:
         file.write(line)
         return True
   except FileExistsError:
      logger.error(f"Error appending to file {file_path}")
      return False

def write_master_station_infos(file_path:str):
   """Write master station static infos in dedicated file"""
   # Write master station header
   line = SEPARATOR + "MASTER STATION INFOS"
   if not append_to_file(file_path=file_path, line=line):
      logger.error(f"Error appending to file {file_path}")
      return

   # Write master station os
   try:
      master_station_os = subprocess.check_output("hostnamectl", shell=True).decode('ascii').strip()
   except:
      # Since hostnamectl doesn't work for WSL
      master_station_os = subprocess.check_output("uname -a", shell=True).decode('ascii').strip()

   line = SEPARATOR + master_station_os
   if not append_to_file(file_path=file_path, line=line):
      logger.error(f"Error appending to file {file_path}")
      return

   # Write master station python version
   python_version = subprocess.check_output("python3 --version", shell=True).decode('ascii').strip()
   line = f"Python version: {python_version}"
   if not append_to_file(file_path=file_path, line=line):
      logger.error(f"Error appending to file {file_path}")
      return

   # Write separator
   line = SEPARATOR
   if not append_to_file(file_path=file_path, line=line):
      logger.error(f"Error appending to file {file_path}")
      return

def write_livebox_infos(ssh: SshClient, file_path:str):
   """Write livebox static infos in dedicated file"""
   # Write livebox header
   line = "LIVEBOX INFOS" + SEPARATOR
   if not append_to_file(file_path=file_path, line=line):
      logger.error(f"Error appending to file {file_path}")
      return

   # Write livebox name
   _splited_dir = file_path.split("/")
   livebox_name = _splited_dir[len(_splited_dir) - 2]
   line = f"Livebox name: {livebox_name}\n\n"
   if not append_to_file(file_path=file_path, line=line):
      logger.error(f"Error appending to file {file_path}")
      return

   # Write Broadcom version
   wl_version = ssh.send_command(cmd="wl ver", method= False, system_cmd=True)
   line = f"Broadcom version: {wl_version}\n\n"
   if not append_to_file(file_path=file_path, line=line):
      logger.error(f"Error appending to file {file_path}")
      return

   # Write network interfaces info
   line = f"Network interfaces:"
   if not append_to_file(file_path=file_path, line=line):
      logger.error(f"Error appending to file {file_path}")
      return
   if_config_result = ssh.send_command(cmd="ifconfig", method= False, system_cmd=True)
   line = f"ifconfig {if_config_result}\n\n"
   if not append_to_file(file_path=file_path, line=line):
      logger.error(f"Error appending to file {file_path}")
      return

   # Write separator
   line = SEPARATOR
   if not append_to_file(file_path=file_path, line=line):
      logger.error(f"Error appending to file {file_path}")
      return

def write_stations_infos(file_path:str):
   """Write conected stations static infos in dedicated file"""
   # Write stations header
   line = "CONNECTED STATIONS INFOS" + SEPARATOR
   if not append_to_file(file_path=file_path, line=line):
      logger.error(f"Error appending to file {file_path}")
      return

   # Write arp table
   arp_table = subprocess.check_output("arp -a", shell=True).decode('ascii').strip()
   line = f"arp -a:  {arp_table}\n\n"
   if not append_to_file(file_path=file_path, line=line):
      logger.error(f"Error appending to file {file_path}")
      return

   # Write separator
   line = SEPARATOR
   if not append_to_file(file_path=file_path, line=line):
      logger.error(f"Error appending to file {file_path}")
      return


def run_static_data(ssh: SshClient, results_dir:str):
   """Entry point to static data program"""

   logger.info("RUNNING PROGRAM: static data")

   # Create static data file
   file_path = f"{results_dir}/{STATIC_DATA_FILE}"

   try:
      with open(file_path, 'x') as file:
         logger.info(f"{file_path} static data file created")
   except FileExistsError:
      logger.error(f"The file '{file_path}' already exists.")

   # write master stations infos
   write_master_station_infos(file_path)

   # write livebox infos
   write_livebox_infos(ssh, file_path)

   # write stations infos
   write_stations_infos(file_path)



