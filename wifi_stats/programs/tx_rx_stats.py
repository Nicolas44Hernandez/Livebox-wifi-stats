"""
Retrieve stats periodicaly for the 2.4 GHz and 5 GHz frequency bands by ussing the command wl counters.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Iterable
from common.telnet import Telnet
import yaml

logger = logging.getLogger(__name__)

RESULTS_FILE_2G =  "tx_rx_2g_stats.txt"
RESULTS_FILE_5G =  "tx_rx_5g_stats.txt"

COMMANDS = {
    "get antena stats": "echo -n 'EE''EE '; wl -i BAND counters; echo 'FF''FF'",
    "check if file exists": "echo -n 'EE''EE '; test -f FILE && echo 'exists'; echo 'FF''FF'",
}

def get_columns(config_file: str):
    """Get results file columns from config file"""

    # Read yml config file
    with open(config_file, "r") as stream:
        try:
            parsed_yaml = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error(exc)

    # Extract data
    columns = parsed_yaml["COLUMNS"]
    return columns

def write_header(telnet: Telnet, columns: Iterable[str], results_dir: str):
    """Write header to results files"""

    # Output redirection to results file
    output_redirection_2g_command = " >> " + results_dir + "/" + RESULTS_FILE_2G
    output_redirection_5g_command = " >> " + results_dir + "/" + RESULTS_FILE_5G

    header = ""
    for i, col in enumerate(columns):
        if i != 0:
            header += "    "
        header += col

    # Write header
    write_header_2g_command = f"echo '{header}' {output_redirection_2g_command}"
    write_header_5g_command = f"echo '{header}' {output_redirection_5g_command}"

    telnet.send_command(write_header_2g_command)
    telnet.send_command(write_header_5g_command)

def retrieve_antena_stats(telnet: Telnet,columns: Iterable[str], band: str):
    """ retrieve and format antena stats """

    # Rereive antena Rx and Tx stats
    antena_stats = retrieve_antena_stats_from_livebox(telnet=telnet, columns=columns, band=band)
    date_time = str(datetime.now())

    # Create entry
    new_entry = f"{antena_stats}    {date_time}"
    return new_entry

def retrieve_antena_stats_from_livebox(telnet: Telnet,columns: Iterable[str], band: str):
    """ retrieve antena stats """

    # Create telnet command
    antena_stats_command =  COMMANDS["get antena stats"]
    if band == "5GHz":
        antena_stats_command = antena_stats_command.replace("BAND", "wl0")
    elif band == "2.4GHz":
        antena_stats_command = antena_stats_command.replace("BAND", "wl2")
    else:
        antena_stats_command = antena_stats_command.replace("BAND", "wl1")

    # Retrieve antena Rx stats
    logger.debug(f"Sending command {antena_stats_command}")
    antena_stats_result_brut = telnet.send_command_and_read_result(antena_stats_command)
    logger.debug(f"Command executed, starting post treatement")

    # Filter retrieved results
    antena_stats_result_lines = str(parse_telnet_output(antena_stats_result_brut)).split("\r\n")[5:15]
    antena_stats_result_dict = {}
    for line in antena_stats_result_lines:
        keys = line.split(" ")[::2]
        values = line.split(" ")[1::2]
        for key, value in zip(keys, values):
            if key in columns:
                antena_stats_result_dict[key]= value

    # Format retrieved results
    antena_stats_result = ""
    txbyte = antena_stats_result_dict["txbyte"]
    rxbyte = antena_stats_result_dict["rxbyte"]
    logger.info(f"BAND: {band} txbyte: {txbyte} rxbyte: {rxbyte}")
    for idx, key in enumerate(columns):
        if key in antena_stats_result_dict:
            if idx == 0:
                antena_stats_result = antena_stats_result_dict[key]
            else:
                antena_stats_result += "    " + antena_stats_result_dict[key]
    logger.debug(f"End post treatement")
    return antena_stats_result

def parse_telnet_output(raw_output: str):
    """Parse the output of the sent command"""
    _splitted_patern = raw_output.split("EEEE")
    return _splitted_patern[len(_splitted_patern) -1].split("FFFF")[0].lstrip()

def run_tx_rx_stats(
    telnet: Telnet,
    results_dir:str,
    analysis_duration_in_minutes: int,
    sampling_period_in_seconds: int,
    columns_config_file: str,
):
    """Entry point for tx_rx_stats program"""

    logger.info("RUNNING PROGRAM: tx_rx stats")
    start = datetime.now()
    estimated_end = start + timedelta(minutes=analysis_duration_in_minutes)
    logger.info(f"Estimated end: {str(estimated_end)}")

    # Get columns
    columns = get_columns(config_file=columns_config_file)

    # Write header
    write_header(telnet=telnet, columns=columns, results_dir=results_dir)

    # Waiting loop
    now = datetime.now()
    while now < estimated_end:
        next_sample_at = now + timedelta(seconds=sampling_period_in_seconds)

        # Retrive antenas stats
        logger.debug("Iteration start")
        new_entry_2g = retrieve_antena_stats(telnet=telnet,columns=columns, band="2.4GHz")
        new_entry_5g = retrieve_antena_stats(telnet=telnet,columns=columns, band="5GHz")
        logger.debug("Statistics retrieved")


        # Write entry in results file
        logger.debug("Writting info in results file")
        output_redirection_2g_command = " >> " + results_dir + "/" + RESULTS_FILE_2G
        output_redirection_5g_command = " >> " + results_dir + "/" + RESULTS_FILE_5G
        write_connected_stations_2g_command = f"echo -e \"{new_entry_2g}\" {output_redirection_2g_command}"
        write_connected_stations_5g_command = f"echo -e \"{new_entry_5g}\" {output_redirection_5g_command}"

        try:
            telnet.send_command(write_connected_stations_2g_command)
            telnet.send_command(write_connected_stations_5g_command)
        except Exception as e:
            logger.error(e)
        now = datetime.now()
        logger.debug("Iteration end")
        while now < next_sample_at:
            time.sleep(0.1)
            now = datetime.now()

