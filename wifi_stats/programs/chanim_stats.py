"""
Retrieve stats periodicaly for the 2.4 GHz and 5 GHz frequency bands by ussing the command wl chanim_stats.
"""

import logging
import time
from datetime import datetime, timedelta
from common.telnet import Telnet

logger = logging.getLogger(__name__)

RESULTS_FILE_2G =  "chanim_stats_2g.txt"
RESULTS_FILE_5G =  "chanim_stats_5g.txt"

COMMANDS = {
    "get header": 'export stats=$(wl -i wl0 chanim_stats | head -2); echo master_station_timestamp | (echo -n -e "$stats \t"  && cat)',
    "get stats 2.4GHz" : 'export stats=$(wl -i wl2 chanim_stats | tail -1); date -Iseconds | (echo -n -e "$stats \t"  && cat)',
    "get stats 5GHz": 'export stats=$(wl -i wl0 chanim_stats | tail -1); date -Iseconds | (echo -n -e "$stats \t"  && cat)',
    "get stats 2.4GHz for log" : "echo -n 'EE''EE '; export stats=$(wl -i wl2 chanim_stats | tail -1); date -Iseconds | (echo -n -e \"$stats \t\"  && cat); echo 'FF''FF'",
    "get stats 5GHz for log" : "echo -n 'EE''EE '; export stats=$(wl -i wl0 chanim_stats | tail -1); date -Iseconds | (echo -n -e \"$stats \t\"  && cat); echo 'FF''FF'",
}


def add_ms_timestamp_to_command(original_command: str):
    """Add master machine timestamp to write command"""
    now = str(datetime.now())
    splitted = original_command.split('-Iseconds')
    new_command = splitted[0] + "-Iseconds; echo " + now + splitted[1]
    return new_command

def parse_telnet_output(raw_output: str):
    """Parse the output of the sent command"""
    _splitted_patern = raw_output.split("EEEE")
    return _splitted_patern[len(_splitted_patern) -1].split("FFFF")[0].lstrip()

def run_chanim_stats(
    telnet: Telnet,
    results_dir:str,
    analysis_duration_in_minutes: int,
    sampling_period_in_seconds: int
):
    """Entry point for chanim stats program"""

    logger.info("RUNNING PROGRAM: chanim stats")
    start = datetime.now()
    estimated_end = start + timedelta(minutes=analysis_duration_in_minutes)
    logger.info(f"Estimated end: {str(estimated_end)}")

    output_redirection_2g_command = " >> " + results_dir + "/" + RESULTS_FILE_2G
    output_redirection_5g_command = " >> " + results_dir + "/" + RESULTS_FILE_5G

    # Write header
    write_header_2g_command = COMMANDS['get header'] + output_redirection_2g_command
    write_header_5g_command = COMMANDS['get header'] + output_redirection_5g_command

    telnet.send_command(write_header_2g_command)
    telnet.send_command(write_header_5g_command)

    get_stats_2G_command = COMMANDS['get stats 2.4GHz'] + output_redirection_2g_command
    get_stats_5G_command = COMMANDS['get stats 5GHz'] + output_redirection_5g_command

    # Waiting loop
    now = datetime.now()
    while now < estimated_end:
        next_sample_at = now + timedelta(seconds=sampling_period_in_seconds)
        try:
            telnet.send_command(add_ms_timestamp_to_command(get_stats_2G_command))
            telnet.send_command(add_ms_timestamp_to_command(get_stats_5G_command))
        except Exception as e:
            logger.error(e)
        now = datetime.now()

        while now < next_sample_at:
            time.sleep(0.1)
            now = datetime.now()

