
from programs.results.traffic_file_generation import generate_requested_throughput_result_file
from programs.results.antenas_througput_file_generation import generate_antenas_real_throughput_result_file
from logging.config import dictConfig
import logging
import argparse
import yaml

logger = logging.getLogger(__name__)

def main():
    """
    Entry point, this method parses the args and run the program
    Args:
        -tf   --transfer_log_file       Transfer log file
        -af   --antenas_log_file        Antenas log file
        -rd   --results_dir             Result generated files dir
        -sc   --stations_config_file    Stations configuration file
        -lc   --logs_configuration      Logs configuration

    """
    parser = argparse.ArgumentParser(prog="WiFi-stats")

    parser.add_argument(
        "-tf",
        "--transfer_log_file",
        type=str,
        help="Transfer log file",
    )

    parser.add_argument(
        "-af",
        "--antenas_log_file",
        type=str,
        help="Antenas log file",
    )

    parser.add_argument(
        "-rd",
        "--results_dir",
        type=str,
        help="Result generated files dir",
    )

    parser.add_argument(
        "-sc",
        "--stations_config_file",
        type=str,
        help="Result generated file",
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

    generate_requested_throughput_result_file(
        log_file=args.transfer_log_file,
        result_file=f"{args.results_dir}/requested_throughput.txt",
        stations_config_file=args.stations_config_file
    )

    generate_antenas_real_throughput_result_file(
        log_file=args.antenas_log_file,
        result_file=f"{args.results_dir}/antenas_real_throughput.txt",
    )

if __name__ == "__main__":
    main()
