"""Wifi stats application"""

import logging
from logging.config import dictConfig
import yaml
import argparse
from common import Telnet
from programs.setup.generate_files import run_generate_random_files
from programs.setup.initial_transfer_files_to_stations import run_initial_files_transfer_to_stations
from programs.setup.generate_traffic_config import run_generate_traffic_config

USB_DEVICE_PATH = "/var/usbmount/kernel::"
RESULTS_DIR = "wifi_stats_results"


logger = logging.getLogger(__name__)


def main():
    """
    Entry point, this method parses the args and calls the wifi stats program
    Args:
        --generate-files                              If pressent generate analysis files
        -sc     --stations_config                     Config file for stations
        -fc     --files_to_send_config                Config file for files transfer program
        -sp     --stations_profile_configuration      Config file for stations profiles
        -nf     --number_of_files_to_send_per_period  Number of files to send
        -p      --number_of_periods                   Number of files to send
        -s      --stations_trafficking                Number of stations trafficking simultaneously
        -tc     --traffic_config_file_name            Name of the traffic config file to generate
        -ti     --traffic_plot_file_name              Name of the traffic plot file to generate
        -lc     --logs_configuration                  Logs configuration
    """
    parser = argparse.ArgumentParser(prog="Generate Files")

    parser.add_argument(
        "--generate-files",
        action="store_true",
    )
    parser.add_argument(
        "-sc",
        "--stations_config",
        type=str,
        help="Config file for stations",
    )

    parser.add_argument(
        "-fc",
        "--files_to_send_config",
        type=str,
        help="Config file for files transfer program",
    )

    parser.add_argument(
        "-sp",
        "--stations_profile_configuration",
        type=str,
        help="Config file for stations profiles",
    )

    parser.add_argument(
        "-nf",
        "--number_of_files_to_send_per_period",
        type=int,
        help="Number of files to send",
    )

    parser.add_argument(
        "-p",
        "--periods",
        type=int,
        help="Number of periods",
    )

    parser.add_argument(
        "-s",
        "--stations_trafficking",
        type=int,
        help="Number of stations trafficking simultaneously",
    )

    parser.add_argument(
        "-tc",
        "--traffic_config_file_name",
        type=str,
        help="Name of the traffic config file to generate",
    )
    parser.add_argument(
        "-ti",
        "--traffic_plot_file_name",
        type=str,
        help="Name of the traffic plot file to generate",
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

    if args.generate_files:
        # Generate files
        run_generate_random_files(stations_config=args.stations_config,
                                  files_to_send_config=args.files_to_send_config)

        # Transfer files to stations
        run_initial_files_transfer_to_stations(
            stations_config=args.stations_config)

    # Generate traffic config
    run_generate_traffic_config(stations_config=args.stations_config,
                                files_to_send_config=args.files_to_send_config,
                                stations_profiles_config=args.stations_profile_configuration,
                                number_of_files_to_send_per_period=args.number_of_files_to_send_per_period,
                                number_of_periods=args.periods,
                                number_of_stations_trafficking_simultaneously=args.stations_trafficking,
                                traffic_config_file_name=args.traffic_config_file_name,
                                traffic_plot_file_name=args.traffic_plot_file_name,
                                )


if __name__ == "__main__":
    main()
