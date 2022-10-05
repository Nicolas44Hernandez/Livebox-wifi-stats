"""
Switch the 5 GHz frequency band on and off at different time intervals by ussing the pcb_cli commands.
"""
import time
import logging
from common.telnet import Telnet
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

RESULTS_FILE_5GH_STATUS =  "band_status_5GHz.txt"

COMMANDS = {
    "pcb command line interface": 'pcb_cli',
    "activate smart wifi": "SSW.Steering.GlobalEnable=1",
    "activate band 2.4GHz": 'NeMo.Intf.rad2g0.Enable=1\n NeMo.Intf.rad2g0.AutoChannelEnable=0\n NeMo.Intf.rad2g0.Channel=11\n NeMo.Intf.rad5g0.Enable=0',
    "activate band 5GHz": 'NeMo.Intf.rad5g0.Enable=1\n NeMo.Intf.rad5g0.AutoChannelEnable=0\n NeMo.Intf.rad5g0.Channel=36',
    "desactivate band 5GHz": 'NeMo.Intf.rad5g0.Enable=0',
}

def activate_smart_wifi(telnet: Telnet):
    """Activate smart wifi in the livebox"""

    # run pcb_line command
    telnet.send_command(COMMANDS['pcb command line interface'])
    # activate smart wifi
    telnet.send_command(COMMANDS['activate smart wifi'])
    # exit pcb_cli
    telnet.send_command("exit")

def activate_band_2_4GHz(telnet: Telnet):
    """Turn on the 2.4GHz wifi band"""

    # run pcb_line command
    telnet.send_command(COMMANDS['pcb command line interface'])
    # activate band 2GHz
    telnet.send_command(COMMANDS['activate band 2.4GHz'])
    # exit pcb_cli
    telnet.send_command("exit")

def log_band_status_change(telnet: Telnet, results_dir: str, new_status: bool):
    """Log the 5GHz wifi band status """

    # Write band activation in status file
    date_time = str(datetime.now())
    status = "ON" if new_status else "OFF"
    logger.info(f"5GHz band: {status}")
    output_redirection_band_activation_command = " >> " + results_dir + "/" + RESULTS_FILE_5GH_STATUS
    log_band_activation_command = f"echo  {date_time} : Wi-Fi 5GHz {status} {output_redirection_band_activation_command}"
    telnet.send_command(log_band_activation_command)


def switch_band_5GHz(telnet: Telnet, new_status: bool):
    """Switch the 5GHz wifi band status """

    status = "activate" if new_status else "desactivate"
    # run pcb_line command
    telnet.send_command(COMMANDS["pcb command line interface"])
    # activate band 5GHz
    telnet.send_command(COMMANDS[f"{status} band 5GHz"])
    # exit pcb_cli
    telnet.send_command("exit")


def run_switch_5GHz(
    telnet: Telnet,
    results_dir:str,
    analysis_duration_in_minutes: int,
    on_period_in_secs,
    off_period_in_secs: int
    ):
    """Entry point to switch 5GHz band program"""

    logger.info("RUNNING PROGRAM: switch 5GHz")

    start = datetime.now()
    estimated_end = start + timedelta(minutes=analysis_duration_in_minutes)
    logger.info(f"Estimated end: {str(estimated_end)}")

    #  activate smart wifi
    activate_smart_wifi(telnet)
    logger.info("Smart wifi ON")

    # activate band 2GHz
    activate_band_2_4GHz(telnet)
    logger.info("2.4GHZ band ON")

    # activate band 5GHz
    switch_band_5GHz(telnet=telnet, new_status=True)
    logger.info(f"5GHz band: ON")
    band_5GHz_is_active = True
    time.sleep(on_period_in_secs)

    # Loop
    now = datetime.now()
    while now < estimated_end:
        # shitch band status
        switch_band_5GHz(telnet=telnet, new_status = not band_5GHz_is_active)
        # set band status control variable
        band_5GHz_is_active = not band_5GHz_is_active
        # log status change
        log_band_status_change(telnet=telnet, results_dir=results_dir, new_status=band_5GHz_is_active)
        # wait until next switch
        time.sleep(on_period_in_secs if band_5GHz_is_active else off_period_in_secs)
        now = datetime.now()

    # set band activated
    switch_band_5GHz(telnet=telnet, new_status=True)

