"""
Telnet connection service
"""
import telnetlib
import socket
import logging
import time
from datetime import date, datetime

logger = logging.getLogger(__name__)

class Telnet:
    """Service class for telnet connection and commands management"""

    def __init__(
        self,
        host: str,
        login: str = None,
        password: str = None,
        telnet_timeout_in_secs: float = 5,
    ):
        self.host = host
        self.login = login
        self.password = password
        self.telnet_timeout_in_secs = telnet_timeout_in_secs
        self.super_user_session = False
        self.time_between_commands = 0.5


    def create_telnet_connection(self):
        """Create telnet connection with host"""

        # try to connect
        try:
            tn_connection = telnetlib.Telnet(
                self.host, timeout=self.telnet_timeout_in_secs
            )
            tn_connection.read_until(b"login: ", timeout=self.telnet_timeout_in_secs)
            login = self.login + "\n"
            # Enter login
            tn_connection.write(login.encode("utf-8"))

            if self.password:
                tn_connection.read_until(b"Password: ", timeout=self.telnet_timeout_in_secs)
                password = self.password + "\n"
                # Enter password
                tn_connection.write(password.encode("utf-8"))
        except (socket.timeout, socket.error):
            logger.error("Telnet connection creation failed")
            return None

        logger.debug(f"Telnet connection established with host: %s", self.host)
        return tn_connection

    def send_command(self, command: str):
        """Send command to telnet host"""
        try:
            connection = self.create_telnet_connection()
            command = command + "\n"
            connection.write(command.encode("ascii"))
            time.sleep(self.time_between_commands)
            connection.write(b"exit\n")
        except Exception as e:
            logger.error(f"Error in telnet connection {e}")


    def send_command_and_read_result(self, command: str):
        """Send command to telnet host and read result"""
        try:
            connection = self.create_telnet_connection()
            command = command + "\n"
            connection.write(command.encode("ascii"))
            time.sleep(self.time_between_commands)
            command_result = connection.read_until(b"FFFF").decode('ascii')
            connection.write(b"exit\n")
            return command_result
        except Exception as e:
            logger.error(f"Error in telnet connection {e}")


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
