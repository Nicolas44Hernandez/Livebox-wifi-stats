
"""
This program plots real traffic seen by the livebox (from the logs counters) for a station.
Must be run after programs execution and results copied in results folder
TODO: Work in progress
"""

from programs.results.plot_traffic import generate_traffic_plots
from logging.config import dictConfig
import logging
import argparse
import yaml

logger = logging.getLogger(__name__)

def main():
    """
    Entry point, this method parses the args and run the program
    Args:
        -rd   --results_dir             Result generated files dir
        -lc   --logs_configuration      Logs configuration

    """
    parser = argparse.ArgumentParser(prog="WiFi-stats")

    parser.add_argument(
        "-rd",
        "--results_dir",
        type=str,
        help="Result generated files dir",
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
    #TODO:  Run for each station
    generate_traffic_plots(station_file=f"{args.results_dir}/station_78_AF_08_31_B1_18.txt", livebox_file=f"{args.results_dir}/tx_rx_2g_stats.txt")


if __name__ == "__main__":
    main()
