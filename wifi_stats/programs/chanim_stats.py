""" Objectif : Récupérer les données sur le flux radio des bandes de fréquences 2,4 GHz et 5 GHz
    Comment  : On se connecte en Telnet à la Livebox et on exécute des commandes (commande principale : wl chanim_stats) dans une boucle afin de récuperer ses données
    Enregistrement sur clé USB :  /var/usbmount/kernel::dev-sdb1/Mes_chanim_stats_2g_30-05-22.txt
                                  /var/usbmount/kernel::dev-sdb1/Mes_chanim_stats_5g_30-05-22.txt
"""

import logging
import time
from datetime import datetime, timedelta
from common.telnet import Telnet

logger = logging.getLogger(__name__)

RESULTS_FILE_2G =  "chanim_stats_2g.txt"
RESULTS_FILE_5G =  "chanim_stats_5g.txt"

COMMANDS = {
    "get header": 'export stats=$(wl -i wl0 chanim_stats | head -2); echo horodatage | (echo -n -e "$stats \t"  && cat)',
    "get stats 2.4GHz" : 'export stats=$(wl -i wl2 chanim_stats | tail -1); date -Iseconds | (echo -n -e "$stats \t"  && cat)',
    "get stats 5GHz": 'export stats=$(wl -i wl0 chanim_stats | tail -1); date -Iseconds | (echo -n -e "$stats \t"  && cat)'
}

def run_chanim_stats(
    telnet: Telnet,
    results_dir:str,
    analysis_duration_in_minutes: int,
    sampling_period_in_seconds: int
):
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
        telnet.send_command(get_stats_2G_command)
        telnet.send_command(get_stats_5G_command)
        now = datetime.now()

        while now < next_sample_at:
            time.sleep(0.1)
            now = datetime.now()

