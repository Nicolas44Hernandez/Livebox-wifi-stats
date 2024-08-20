"""Calibrate station for measurement campaign"""

import logging
from logging.config import dictConfig
import yaml
import argparse
from common import SshClient
from programs.calibration.initial_calibrate_stations import run_calibrate_station


logger = logging.getLogger(__name__)


def main():
    """
    Entry point, this method parses the args and calls the wifi stats program
    Args:
        -n      --name                     Livebox name
        -l      --livebox                  Livebox ip address
        -u      --user                     Telnet connection user
        -pw     --password                 Telnet connection password
        -lc     --logs_config              Logs configuration
        -sm     --station_to_calibrate_mac Station to calibrate mac address
    """
    parser = argparse.ArgumentParser(prog="Calibrate WiFi-stats")

    parser.add_argument(
        "-n",
        "--name",
        type=str,
        help="Livebox name",
    )

    parser.add_argument(
        "-l",
        "--livebox",
        type=str,
        help="Livebox ip address",
    )

    parser.add_argument(
        "-u",
        "--user",
        type=str,
        help="User",
    )

    parser.add_argument(
        "-pw",
        "--password",
        type=str,
        help="Password",
    )

    parser.add_argument(
        "-sm",
        "--station_to_calibrate_mac",
        type=str,
        help="Station to calibrate mac address",
    )

    parser.add_argument(
        "-lc",
        "--logs_configuration",
        type=str,
        help="Logs config",
    )

    # Parse args
    args = parser.parse_args()

    # Load logging configuration
    with open(args.logs_configuration) as stream:
        dictConfig(yaml.full_load(stream))

    logger.info(f"Running program Calibrate station")
    logger.info(f"args: {args}")

    # Create ssh interface
    ssh = SshClient(host=args.livebox, user=args.user, password=args.password)

    run_calibrate_station(ssh=ssh, station_mac=args.station_to_calibrate_mac)


if __name__ == "__main__":
    main()
