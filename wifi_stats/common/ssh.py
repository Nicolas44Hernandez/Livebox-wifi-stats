"""
SSH connection service
"""
import re
from fabric import Connection
import socket
import logging
import time
from datetime import date, datetime

logger = logging.getLogger(__name__)

class SshClient:
    """Service class for ssh connection and commands management"""

    def __init__(
        self,
        host: str,
        port: int = 22,
        user: str = None,
        password: str = None,
        timeout_in_secs: float = 5,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.timeout_in_secs = timeout_in_secs
        self.connection = self.create_connection()

    def create_connection(self):
        """Create ssh connection with host"""

        # try to connect
        try:
            connection = Connection(
                host=self.host,
                port=self.port,
                user=self.user,
                connect_kwargs={"password": self.password},
                connect_timeout=self.timeout_in_secs
            )
        except Exception:
            logger.error("SSH connection creation failed")
            return None

        return connection

    def close(self):
        try:
            if not self.connection:
                logger.error("SSH connection not stablished")
                return None
            self.connection.close()
        except Exception:
            logger.error("Error in SSH connection")
        logger.debug(f"SSH connection closed with host: %s", self.host)

    def send_command(self, cmd: str, method: bool = False) -> str:
        """Send command to SSH host"""
        try:
            # build ubus-cli command
            intro = "ubus-cli \""
            end = " ?\""
            command = f"{intro}{cmd}{end}"
            if not self.connection:
                logger.error("SSH connection not stablished")
                return None
            result = self.connection.run(command, hide=True)
            #logger.info(f"command: '{result.command}' result: '{result.stdout}'")

            # Remove extra chars
            raw_result = ""
            if method:
                raw_result = result.stdout.split("returned\n")[1].split("\n\n\n\n")[0]
            else:
                _separator = f"{cmd} ?\n"
                raw_result = result.stdout.split("\n\n\n\n")[0].split(_separator)[1]
            return raw_result
        except Exception as e:
            logger.error(e)


    def create_results_dir(self, timestamp:str, device: str, results_directory: str, box_name: str):
        """
        Create a clean dir for telnet results, if directory exists files will be overwritten
        """

        box_directory = results_directory + "/" + box_name
        analysis_results_directory = box_directory + "/" + timestamp
        create_dir_command = "mkdir " + device + results_directory + "\n"
        create_box_dir_command = "mkdir " + device + box_directory + "\n"
        create_analysis_dir_command = "mkdir " + device + analysis_results_directory + "\n"
        try:
            connection = self.create_telnet_connection()
            connection.write(create_dir_command.encode("ascii"))
            time.sleep(self.time_between_commands)
            connection.write(create_box_dir_command.encode("ascii"))
            time.sleep(self.time_between_commands)
            connection.write(create_analysis_dir_command.encode("ascii"))
            time.sleep(self.time_between_commands)
        except (socket.timeout, socket.error):
            logger.error("Error in telnet connection")
            return None
        return device + analysis_results_directory
