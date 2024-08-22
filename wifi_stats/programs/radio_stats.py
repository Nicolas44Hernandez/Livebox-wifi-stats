"""
Retrieve livebox radio stats periodicaly for the 2.4 GHz and 5 GHz frequency bands.
"""

import logging
import time
import yaml
from datetime import datetime, timedelta
from common import SshClient

logger = logging.getLogger(__name__)

RESULTS_FILE_RADIO_STATS_2G =  "livebox_radio_stats_2g.txt"
RESULTS_FILE_RADIO_STATS_5G =  "livebox_radio_stats_5g.txt"
RESULTS_FILE_RADIO_AIR_STATS_2G =  "livebox_radio_air_stats_2g.txt"
RESULTS_FILE_RADIO_AIR_STATS_5G =  "livebox_radio_air_stats_5g.txt"

COMMANDS = {
    "get radio stats": "WiFi.Radio.*.getRadioStats()",
    "get radio air stats": "WiFi.Radio.*.getRadioAirStats()",
}

RADIO = {"2.4GHz":"1", "5GHz": "2"}

def create_file(file_path:str):
    """Create static data file"""
    try:
        with open(file_path, 'x'):
            logger.info(f"{file_path} file created")
            return True
    except FileExistsError:
        logger.error(f"The file '{file_path}' already exists.")
        return False


def append_to_file(file_path: str, line: str) -> bool:
   """Append str to file"""
   try:
      with open(file_path, 'a') as file:
         file.write(line)
         return True
   except FileExistsError:
      logger.error(f"Error appending to file {file_path}")
      return False


def get_columns(config_file: str):
    """Get results file columns from config file"""

    # Read yml config file
    with open(config_file, "r") as stream:
        try:
            parsed_yaml = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error(exc)

    # Extract data
    radio_stats_columns = parsed_yaml["RADIO_STATS_COLUMNS"]
    radio_air_stats_columns = parsed_yaml["RADIO_AIR_STATS_COLUMNS"]

    return radio_stats_columns, radio_air_stats_columns


def add_ms_timestamp_to_command(original_command: str):
    """Add master machine timestamp to write command"""
    now = str(datetime.now())
    splitted = original_command.split('-Iseconds')
    new_command = splitted[0] + "-Iseconds; echo " + now + splitted[1]
    return new_command


def parse_radio_stats(radio_stats: str, columns: dict) -> dict:
    """Parse radio stats results to dict"""
    parsed_stats = {}

    # Extract simple stats
    simple_stats = radio_stats.split("\n")
    # Extract composed stats
    _composed_lines = radio_stats.split("Wmm")
    _composed_stats = []
    for line in _composed_lines:
        if "}" in line:
             _composed_stats.append(f"Wmm{line}")

    for key in columns:
        if "." not in key:
            #Append simple stats
            for stat_line in simple_stats:
                if key in stat_line:
                    value = stat_line.split("= ")[1][:-1]
                    parsed_stats[key] = value
                    break
        else:
            # Append composed stats
            global_key, inner_key = key.split(".")
            for stat_line in _composed_stats:
                if global_key in stat_line:
                    if inner_key in stat_line:
                        value = stat_line.split(f"{inner_key} = ")[1].split(",")[0]
                        if "VO" in inner_key:
                            value = value.split("\n        }")[0]
                        parsed_stats[key] = value
                        break

    return parsed_stats


def parse_radio_air_stats(radio_air_stats: str, columns: dict) -> dict:
    """Parse radio air stats results to dict"""
    parsed_stats = {}

    # Extract simple stats
    simple_stats = radio_air_stats.split("\n")
    # Extract composed stats
    _composed_lines = radio_air_stats.split("Vendor")
    _composed_stats = []
    for line in _composed_lines:
        if "}" in line:
             _composed_stats.append(f"Vendor{line}")

    for key in columns:
        if "." not in key:
            #Append simple stats
            for stat_line in simple_stats:
                if key in stat_line:
                    value = stat_line.split("= ")[1][:-1]
                    parsed_stats[key] = value
                    break
        else:
            # Append composed stats
            global_key, inner_key = key.split(".")
            for stat_line in _composed_stats:
                if global_key in stat_line:
                    if inner_key in stat_line:
                        value = stat_line.split(f"{inner_key} = ")[1].split(",")[0]
                        if "Glitch" in inner_key:
                            value = value.split("\n        }")[0]
                        parsed_stats[key] = value
                        break

    return parsed_stats


def append_results_to_file(stats: dict, columns:dict, file_path: str, timestamp: str) -> bool:
    """Append dict to results file"""
    # Create new entry with stat
    with open(file_path, 'a') as file:
        new_entry = ""
        for key in columns:
            if key in stats:
                new_entry += f"{stats[key]}\t"
            else:
                new_entry += f"None\t"
        new_entry += f"{timestamp}\n"
        # Append new entry to file
        file.write(new_entry)



def run_radio_stats(
    ssh: SshClient,
    results_dir:str,
    columns_config_file: str,
    analysis_duration_in_minutes: int,
    sampling_period_in_seconds: int
):
    """Entry point for radio stats program"""

    logger.info("RUNNING PROGRAM: radio stats")
    start = datetime.now()
    estimated_end = start + timedelta(minutes=analysis_duration_in_minutes)
    logger.info(f"Estimated end: {str(estimated_end)}")

    # Create files
    results_file_radio_stats_2g_path = f"{results_dir}/{RESULTS_FILE_RADIO_STATS_2G}"
    results_file_radio_stats_5g_path = f"{results_dir}/{RESULTS_FILE_RADIO_STATS_5G}"
    results_file_radio_air_stats_2g_path = f"{results_dir}/{RESULTS_FILE_RADIO_AIR_STATS_2G}"
    results_file_radio_air_stats_5g_path = f"{results_dir}/{RESULTS_FILE_RADIO_AIR_STATS_5G}"

    if (not create_file(results_file_radio_stats_2g_path) or
        not create_file(results_file_radio_stats_5g_path) or
        not create_file(results_file_radio_air_stats_2g_path) or
        not create_file(results_file_radio_air_stats_5g_path)):
        logger.error("Error in file creation")
        return

    # get table columns
    radio_stats_columns, radio_air_stats_columns = get_columns(config_file=columns_config_file)

    # Write radio stats headers
    header = ""
    for key in radio_stats_columns:
        header+=f"{key}\t"
    header+=f"datetime\n"

    if not append_to_file(file_path=results_file_radio_stats_2g_path, line=header):
        logger.error(f"Error appending to file {results_file_radio_stats_2g_path}")
        return
    if not append_to_file(file_path=results_file_radio_stats_5g_path, line=header):
        logger.error(f"Error appending to file {results_file_radio_stats_5g_path}")
        return

    # Write radio air stats headers
    header = ""
    for key in radio_air_stats_columns:
        header+=f"{key}\t"
    header+=f"datetime\n"

    if not append_to_file(file_path=results_file_radio_air_stats_2g_path, line=header):
        logger.error(f"Error appending to file {results_file_radio_air_stats_2g_path}")
        return
    if not append_to_file(file_path=results_file_radio_air_stats_5g_path, line=header):
        logger.error(f"Error appending to file {results_file_radio_air_stats_5g_path}")
        return

    # Waiting loop
    now = datetime.now()
    while now < estimated_end:
        next_sample_at = now + timedelta(seconds=sampling_period_in_seconds)
        try:
            # Retrieve radio stats
            cmd = COMMANDS["get radio stats"]
            radio_stats_raw = ssh.send_command(cmd=cmd, method= False)
            radio_stats_timestamp = str(datetime.now())
            # Parse return values
            _separator_2g = f"WiFi.Radio.{RADIO['2.4GHz']}.getRadioStats() returned\n"
            _separator_5g = f"WiFi.Radio.{RADIO['5GHz']}.getRadioStats() returned\n"
            _separator_end = f"\n]\nWiFi."
            radio_stats_2g = parse_radio_stats(radio_stats_raw.split(_separator_2g)[1].split(_separator_end)[0], radio_stats_columns)
            radio_stats_5g = parse_radio_stats(radio_stats_raw.split(_separator_5g)[1].split(_separator_end)[0], radio_stats_columns)

            # Retrieve radio air stats
            cmd = COMMANDS["get radio air stats"]
            radio_air_stats_raw = ssh.send_command(cmd=cmd, method= False)
            radio_air_stats_timestamp = str(datetime.now())
            # Parse return values
            _separator_2g = f"WiFi.Radio.{RADIO['2.4GHz']}.getRadioAirStats() returned\n"
            _separator_5g = f"WiFi.Radio.{RADIO['5GHz']}.getRadioAirStats() returned\n"
            _separator_end = f"\n]\nWiFi."
            radio_air_stats_2g = parse_radio_air_stats(radio_air_stats_raw.split(_separator_2g)[1].split(_separator_end)[0], radio_air_stats_columns)
            radio_air_stats_5g = parse_radio_air_stats(radio_air_stats_raw.split(_separator_5g)[1].split(_separator_end)[0], radio_air_stats_columns)


            # Write values in result files
            append_results_to_file(
                stats=radio_stats_2g,
                columns=radio_stats_columns,
                file_path=results_file_radio_stats_2g_path,
                timestamp=radio_stats_timestamp,
            )
            append_results_to_file(
                stats=radio_stats_5g,
                columns=radio_stats_columns,
                file_path=results_file_radio_stats_5g_path,
                timestamp=radio_stats_timestamp,
            )
            append_results_to_file(
                stats=radio_air_stats_2g,
                columns=radio_air_stats_columns,
                file_path=results_file_radio_air_stats_2g_path,
                timestamp=radio_air_stats_timestamp,
            )
            append_results_to_file(
                stats=radio_air_stats_5g,
                columns=radio_air_stats_columns,
                file_path=results_file_radio_air_stats_5g_path,
                timestamp=radio_air_stats_timestamp,
            )

        except Exception as e:
            logger.error(e)
        now = datetime.now()

        while now < next_sample_at:
            time.sleep(0.1)
            now = datetime.now()

