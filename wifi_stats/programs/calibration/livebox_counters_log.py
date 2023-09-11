"""
Log livebox counters
"""

from datetime import datetime, timedelta
import logging
import time
from common.telnet import Telnet
from programs.tx_rx_stats import retrieve_antena_stats_from_livebox


logger = logging.getLogger(__name__)


COMMANDS = {
    "get antena stats": "echo -n 'EE''EE '; wl -i BAND counters; echo 'FF''FF'",
}

VALUES_TO_LOG = ["txbyte", "rxbyte"]


def run_log_livebox_counters(
    telnet: Telnet,
):
    """Entry point for initial log livebox counters program"""

    logger.info(
        f"RUNNING PROGRAM: Log livebox counters VALUES_TO_LOG: {VALUES_TO_LOG}")

    now = datetime.now()

    while True:
        next_sample_at = now + timedelta(seconds=1)

        # Get bands counters
        counters_2GHz = retrieve_antena_stats_from_livebox(telnet=telnet, columns=VALUES_TO_LOG, band="2.4GHz")
        txbytes_2GHz, rxbytes_2GHz = counters_2GHz.split("    ")
        counters_5GHz = retrieve_antena_stats_from_livebox(telnet=telnet, columns=VALUES_TO_LOG, band="5GHz")
        txbytes_5GHz, rxbytes_5GHz = counters_5GHz.split("    ")

        # log results
        logger.info(f"txbytes_2GHz:{txbytes_2GHz}   rxbytes_2GHz:{rxbytes_2GHz}  txbytes_5GHz:{txbytes_5GHz}   rxbytes_5GHz:{rxbytes_5GHz}")

        now = datetime.now()

        while now < next_sample_at:
            time.sleep(0.1)
            now = datetime.now()
