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
from programs.tx_rx_stats import run_tx_rx_stats

USB_DEVICE_PATH = "/var/usbmount/kernel::"
RESULTS_DIR = "wifi_stats_results"


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
        -scf    --stations_config          Config file for stations
        -tcf    --traffic_config           Config file for analysis traffic
        -ts     --timestamp                Analysis timestamp for results file
        -sc     --stations_columns_config  Config file for the result table in info stations program
        -ac     --antenas_columns_config   Config file for the result table in tx_rx_stats program
        -d      --duration                 Analysis duration in mins
        -td     --transfert_duration       Transfert duration in secs
        -sp     --sampling_period_in_secs  Sampling period for information request
        -on     --on_period_in_secs        5GHz band ON period in secs
        -off    --off_period_in_secs       5GHz band OFF period in secs
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
        "-scf",
        "--stations_config",
        type=str,
        help="Config file for stations",
    )

    parser.add_argument(
        "-tcf",
        "--traffic_config_file",
        type=str,
        help="Config file for analysis traffic",
    )

    parser.add_argument(
        "-ts",
        "--timestamp",
        type=str,
        help="Analysis timestamp for results file",
    )

    parser.add_argument(
        "-sc",
        "--stations_columns_config",
        type=str,
        help="Config file for the result table in info stations program",
    )

    parser.add_argument(
        "-ac",
        "--antenas_columns_config",
        type=str,
        help="Config file for the result table in tx_rx_stats program",
    )

    parser.add_argument(
        "-d",
        "--duration",
        type=int,
        help="Analysis duration in minutes",
    )

    parser.add_argument(
        "-td",
        "--transfert_duration",
        type=int,
        help="Transfert duration in seconds",
    )

    parser.add_argument(
        "-sp",
        "--sampling_period_in_secs",
        type=int,
        help="Sampling period for information request",
    )

    parser.add_argument(
        "-on",
        "--on_period_in_secs",
        type=int,
        help="5GHz band ON period in secs",
    )

    parser.add_argument(
        "-off",
        "--off_period_in_secs",
        type=int,
        help="5GHz band ON period in secs",
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

    if args.program == "files_transfer":
        run_files_transfer(
            stations_config=args.stations_config,
            traffic_config_file=args.traffic_config_file,
            analysis_duration_in_minutes=args.duration,
            transfert_duration_in_secs=args.transfert_duration
        )
        return

    # Create telnet instance
    telnet = Telnet(host=args.livebox, login=args.user, password=args.password)

    # Create results dir
    device = f"/var/usbmount/kernel::{args.results_disk}/"
    results_dir = telnet.create_results_dir(
        timestamp=args.timestamp, device=device, results_directory=RESULTS_DIR, box_name=args.name)

    # Run program
    if args.program == "static_livebox_data":
        run_static_data(telnet=telnet, results_dir=results_dir)
        return

    if args.program == "switch_5GHz":
        run_switch_5GHz(
            telnet=telnet,
            results_dir=results_dir,
            analysis_duration_in_minutes=args.duration,
            on_period_in_secs=args.on_period_in_secs,
            off_period_in_secs=args.off_period_in_secs,
        )
        return

    if args.program == "chanim_stats":
        run_chanim_stats(
            telnet=telnet,
            results_dir=results_dir,
            analysis_duration_in_minutes=args.duration,
            sampling_period_in_seconds=args.sampling_period_in_secs
        )
        return

    if args.program == "stations":
        run_info_connected_stations(
            telnet=telnet,
            results_dir=results_dir,
            analysis_duration_in_minutes=args.duration,
            sampling_period_in_seconds=args.sampling_period_in_secs,
            columns_config_file=args.stations_columns_config,
        )
        return

    if args.program == "antenas":
        run_tx_rx_stats(
            telnet=telnet,
            results_dir=results_dir,
            analysis_duration_in_minutes=args.duration,
            sampling_period_in_seconds=args.sampling_period_in_secs,
            columns_config_file=args.antenas_columns_config,
        )
        return


if __name__ == "__main__":
    main()
