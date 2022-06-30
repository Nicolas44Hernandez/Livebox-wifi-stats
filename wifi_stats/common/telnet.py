
import telnetlib
import socket
import logging
import time
from datetime import date

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
        self.connection = self.create_telnet_connection()
        self.super_user_session = False
        self.time_between_commands = 0.2

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

    def close(self):
        try:
            self.connection.write(b"exit\n")
        except (socket.timeout, socket.error):
            logger.error("Error in telnet connection")
        logger.debug(f"Telnet connection closed with host: %s", self.host)

    def send_command(self, command: str):
        """Send command to telnet host"""
        try:
            command = command + "\n"
            self.connection.write(command.encode("ascii"))
            time.sleep(self.time_between_commands)
        except (socket.timeout, socket.error):
            logger.error("Error in telnet connection")

    def create_results_dir(self, device: str, results_directory: str, box_name: str):
        """Create a clean dir for telnet results, if directory exists files will be overwritten"""
        # create wifi stats results dir if doesnt exists
        box_directory = results_directory + "/" + box_name
        today_results_directory = box_directory + "/" + str(date.today())
        create_dir_command = "mkdir " + device + results_directory + "\n"
        create_box_dir_command = "mkdir " + device + box_directory + "\n"
        create_today_dir_command = "mkdir " + device + today_results_directory + "\n"
        clean_dir_command = "rm -f -r "  + device + today_results_directory + "/*\n"
        try:
            self.connection.write(create_dir_command.encode("ascii"))
            time.sleep(self.time_between_commands)
            self.connection.write(create_box_dir_command.encode("ascii"))
            time.sleep(self.time_between_commands)
            self.connection.write(create_today_dir_command.encode("ascii"))
            time.sleep(self.time_between_commands)
            self.connection.write(clean_dir_command.encode("ascii"))
            time.sleep(self.time_between_commands)
        except (socket.timeout, socket.error):
            logger.error("Error in telnet connection")
            return None

        return device + today_results_directory
