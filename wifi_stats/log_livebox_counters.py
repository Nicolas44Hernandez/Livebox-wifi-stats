"""Log livebox counters application"""

import logging
from logging.config import dictConfig
import yaml
import argparse
from common import Telnet
from programs.calibration.livebox_counters_log import run_log_livebox_counters

USB_DEVICE_PATH = "/var/usbmount/kernel::"

logger = logging.getLogger(__name__)


def main():
    """
    Entry point, this method parses the args and calls the wifi stats program
    Args:
        -l      --livebox                  Livebox ip address
        -u      --user                     Telnet connection user
        -pw     --password                 Telnet connection password
        -lc     --logs_config              Logs configuration
    """
    parser = argparse.ArgumentParser(prog="Calibrate WiFi-stats")

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

    logger.info(f"Running program Log livebox counters station")
    logger.info(f"args: {args}")

    # Create telnet instance
    telnet = Telnet(host=args.livebox, login=args.user, password=args.password)

    run_log_livebox_counters(telnet=telnet)

if __name__ == "__main__":
    main()
