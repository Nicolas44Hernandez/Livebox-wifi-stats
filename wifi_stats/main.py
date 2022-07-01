"""Wifi stats application"""

import logging
from logging.config import dictConfig
import yaml
import argparse
from common import Telnet
from programs.chanim_stats import run_chanim_stats
from programs.static_data import run_static_data
from programs.info_connected_stations import run_info_connected_stations
from programs.switch_5GHz import run_switch_5GHz
from programs.files_transfer import run_files_transfer
from programs.generate_random_files import run_generate_random_files



# Connection params
HOST = "192.168.1.1"
USER = 'root'
PASSWORD = "sah"
USB_DEVICE_PATH = "/var/usbmount/kernel::"
RESULTS_DIR = "wifi_stats_results"

PROGRAMS = {
    "chanim_stats": run_chanim_stats,
    "static_livebox_data": run_static_data,
    "stations": run_info_connected_stations,
    "switch_5GHz": run_switch_5GHz,
    "files_transfer": run_files_transfer,
}

logging.basicConfig(format='%(asctime)s [%(threadName)s] [%(levelname)s] %(name)s: %(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)

def main():
    """
    Entry point, this method parses the args and calls the wifi stats program
    Args:
        -p      --program                  Program to run
        -n      --name                     Livebox name
        -l      --livebox                  Livebox ip address
        -u      --user                     Telnet connection user
        -pw     --password                 Telnet connection password
        -f      --files_path               Random files path
        -fc     --files_transfer_config    Config file for files transfer program
        -d      --duration                 Analysis duration
        -lc     --logs_config              Logs configuration
        -rd     --results_disk             External USB disk for analysis results
    """
    parser = argparse.ArgumentParser(prog="WiFi-stats")

    parser.add_argument(
        "-p",
        "--program",
        type=str,
        help="Program to run",
    )

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
        "-f",
        "--files_path",
        type=str,
        help="Random files path (Only to generate random files)",
    )

    parser.add_argument(
        "-fc",
        "--files_transfer_config",
        type=str,
        help="Config file for files transfer program",
    )

    parser.add_argument(
        "-d",
        "--duration",
        type=int,
        help="Analysis duration in minutes",
    )

    parser.add_argument(
        "-lc",
        "--logs_config",
        type=str,
        help="Logs config",
    )

    parser.add_argument(
        "-rd",
        "--results_disk",
        type=str,
        help="External USB disk for analysis results",
    )

    # Parse args
    args = parser.parse_args()

    # Load logging configuration
    with open(args.logs_config) as stream:
        dictConfig(yaml.full_load(stream))

    logger.info(f"Running program: {args.program}")
    logger.info(f"args: {args}")

    # Only for generate random files
    if args.program == "generate_random_files":
        run_generate_random_files(files_path=args.files_path)
        return

     # Only for files_transfer
    if args.program == "files_transfer":
        run_files_transfer(config_file=args.files_transfer_config, duration_in_minutes=args.duration)
        return

    # Create telnet connection
    telnet = Telnet(host=args.livebox, login=args.user, password=args.password)

    if telnet.connection is None:
        logger.error("Error creating telnet connection, check connection params")
        return

    # Create results dir
    device = f"/var/usbmount/kernel::{args.results_disk}/"
    results_dir = telnet.create_results_dir(device=device, results_directory=RESULTS_DIR, box_name = args.name)

    # Run program
    if args.program in PROGRAMS:
        PROGRAMS[args.program](telnet=telnet, results_dir=results_dir, duration_in_minutes=args.duration)

if __name__ == "__main__":
    main()
