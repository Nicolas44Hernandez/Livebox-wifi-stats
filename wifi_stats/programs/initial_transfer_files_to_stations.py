"""
Initial transfer files to stations
"""

import os
import logging
import pexpect
from programs.files_transfer import get_test_params

logger = logging.getLogger(__name__)


def create_directory(station, directory: str):
    """Create directory in stations to put the files"""
    # Get station params
    station_name = station["name"]
    station_ip = station["ip"]
    ssh_usr = station["ssh_user"]
    ssh_password = station["ssh_password"]
    transfer_protocol = station["protocol"]
    port = station["port"]
    operative_system = station["operative_system"]

    logger.info(
        f"Creating directory {directory} for station:{station_name} OS:{operative_system}")

    if transfer_protocol == "scp":
        # Create directory via SSH
        if operative_system == "Windows":
            # Empty directory
            command = (
                f"sshpass -p '{ssh_password}' ssh {ssh_usr}@{station_ip} 'del /Q files_transfer\{directory}\*'"
            )
            os.system(command)
            # Create directory if doesnt exists
            command = (
                f"sshpass -p '{ssh_password}' ssh {ssh_usr}@{station_ip} 'mkdir files_transfer\{directory}'"
            )
            os.system(command)
        elif operative_system == "Linux":
            # Remove directory
            command = (
                f"sshpass -p '{ssh_password}' ssh {ssh_usr}@{station_ip} 'rm -r files_transfer/{directory}'"
            )
            os.system(command)
            # Create directory
            command = (
                f"sshpass -p '{ssh_password}' ssh {ssh_usr}@{station_ip} 'mkdir -p files_transfer/{directory}'"
            )
            os.system(command)
        return

    elif transfer_protocol == "sftp":
        # Create directory via SFTP
        cmd1 = (
            f"sshpass -p '{ssh_password}' sftp -P {port} -oHostKeyAlgorithms=+ssh-rsa {ssh_usr}@{station_ip}:/files/"
        )
        child = pexpect.spawn(cmd1)
        child.expect("sftp> ")
        # remove old directory and content
        cmd = f"rm {directory}/*"
        child.sendline(cmd)
        child.expect("sftp> ")
        cmd = f"rmdir {directory}"
        child.sendline(cmd)
        child.expect("sftp> ")

        # Create new directory
        cmd2 = f"mkdir {directory}"
        child.sendline(cmd2)
        child.expect("sftp> ")
        child.sendline("exit")
        child.close()


def send_files_to_station(station, files_path: str, directory: str):
    """Send files to transfer to connected station"""

    # Get station params
    station_ip = station["ip"]
    ssh_usr = station["ssh_user"]
    ssh_password = station["ssh_password"]
    transfer_protocol = station["protocol"]
    port = station["port"]

    files_to_send = os.listdir(files_path)
    logger.info(f"files_path: {files_path}")
    logger.info(f"files_to_send: {files_to_send}")

    for _file in sorted(files_to_send):
        _log_line = f"Sending file {_file} to {station_ip} protocol:{transfer_protocol}"
        logger.info(_log_line)
        if transfer_protocol == "scp":
            # SCP send file
            command = (
                f"sshpass -p '{ssh_password}' scp {files_path}/{_file} {ssh_usr}@{station_ip}:files_transfer/{directory}"
            )
            # Run command
            os.system(command)

        elif transfer_protocol == "sftp":
            # SCTP file transfer to station
            cmd1 = (
                f"sshpass -p '{ssh_password}' sftp -P {port} -oHostKeyAlgorithms=+ssh-rsa {ssh_usr}@{station_ip}:/files/{directory}/"
            )
            child = pexpect.spawn(cmd1)
            child.expect("sftp> ")
            cmd2 = f"put {files_path}/{_file}"
            child.sendline(cmd2)
            child.expect("sftp> ")
            child.sendline("exit")
            child.close()
        logger.info("File sent")


def run_initial_files_transfer_to_stations(config_file: str):
    """Entry point for initial transfer files program"""

    logger.info("RUNNING PROGRAM: Initial transfer files to stations")

    stations_dict, files_path = get_test_params(config_file=config_file)
    directory = files_path.split('/')[-2]

    for station in stations_dict:
        # Create directory in station
        create_directory(station=station, directory=directory)

        # Send files to station
        station_name = station["name"]
        files_dir = f"{files_path}/{station_name}"
        send_files_to_station(
            station=station, files_path=files_dir, directory=directory
        )
