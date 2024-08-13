"""
This program plots real traffic seen by the livebox (from the logs counters) for a station.
Must be run after programs execution and results copied in results folder
TODO: Work in progress
"""
import matplotlib.pyplot as plt
import numpy as np
import logging

SEPARATOR="    "

logger = logging.getLogger(__name__)


def generate_stations_plots(station_file: str):
    """Plot station traffic file"""
    lines = []
    col_names = []
    rx_bytes = []
    tx_bytes = []
    rx_throughput = [0]
    tx_throughput = [0]
    total_throughput = [0]

    f = open(station_file, "r")
    for i, x in enumerate(f):
        if i == 0:
            col_names = x.split(SEPARATOR)
            continue
        lines.append(x.split(SEPARATOR))

    tx_bytes_idx = col_names.index("tx total bytes")
    rx_bytes_idx = col_names.index("rx data bytes")

    for line in lines:
        tx_bytes.append(int(line[tx_bytes_idx].split("sent: ")[1]))
        rx_bytes.append(int(line[rx_bytes_idx]))

    # Get Tx throughput
    for idx, tx_ in enumerate(tx_bytes):
        if idx > 0:
            sent_Mb = (tx_ - tx_bytes[idx -1]) * (8/1e6)
            throughput_Mbps = sent_Mb / 5
            tx_throughput.append(throughput_Mbps)

    # Get Rx throughput
    for idx, rx_ in enumerate(rx_bytes):
        if idx > 0:
            sent_Mb = (rx_ - rx_bytes[idx -1]) * (8/1e6)
            throughput_Mbps = sent_Mb / 5
            rx_throughput.append(throughput_Mbps)

    # Get Total throughput
    for idx, rx_ in enumerate(rx_bytes):
        if idx > 0:
            total_throughput.append(tx_throughput[idx] + rx_throughput[idx])


    # Plot traffic
    fig1, axs = plt.subplots(2)

    arrays_len = len(rx_throughput)
    x = range(0, arrays_len, 1)

    # Plot tx troughtput
    label = "tx_throughput"
    axs[0].scatter(x, tx_throughput, color='blue', label=f"{label}")
    label = "rx_throughput"
    axs[0].scatter(x, rx_throughput, color='green', label=f"{label}")

    fig1.suptitle('Station throughput', fontsize=12)
    axs[0].legend(loc='upper center', ncol=2)
    axs[0].grid()


    # Subplot total throughput
    label = "total_throughput"
    axs[1].scatter(x, total_throughput, color='black', label=f"{label}")
    axs[1].legend(loc='upper center')
    axs[1].grid()


    #plt.show()


def generate_livebox_plots(livebox_file: str):
    """Plot station traffic file"""
    lines = []
    col_names = []
    rx_bytes = []
    tx_bytes = []
    rx_throughput = [0]
    tx_throughput = [0]
    total_throughput = [0]

    f = open(livebox_file, "r")
    for i, x in enumerate(f):
        if i == 0:
            col_names = x.split(SEPARATOR)
            continue
        lines.append(x.split(SEPARATOR))

    tx_bytes_idx = col_names.index("txbyte")
    rx_bytes_idx = col_names.index("rxbyte")

    for line in lines:
        tx_bytes.append(int(line[tx_bytes_idx]))
        rx_bytes.append(int(line[rx_bytes_idx]))

    # Get Tx throughput
    for idx, tx_ in enumerate(tx_bytes):
        if idx > 0:
            sent_Mb = (tx_ - tx_bytes[idx -1]) * (8/1e6)
            if sent_Mb < 0 :
                sent_Mb = 0
            throughput_Mbps = sent_Mb / 5
            tx_throughput.append(throughput_Mbps)

    # Get Rx throughput
    for idx, rx_ in enumerate(rx_bytes):
        if idx > 0:
            sent_Mb = (rx_ - rx_bytes[idx -1]) * (8/1e6)
            if sent_Mb < 0 :
                sent_Mb = 0
            throughput_Mbps = sent_Mb / 5
            rx_throughput.append(throughput_Mbps)

    # Get Total throughput
    for idx, rx_ in enumerate(rx_bytes):
        if idx > 0:
            total_throughput.append(tx_throughput[idx] + rx_throughput[idx])


    # Plot traffic
    fig1, axs = plt.subplots(2)

    arrays_len = len(rx_throughput)
    x = range(0, arrays_len, 1)

    # Plot tx troughtput
    label = "tx_throughput"
    axs[0].scatter(x, tx_throughput, color='blue', label=f"{label}")
    label = "rx_throughput"
    axs[0].scatter(x, rx_throughput, color='green', label=f"{label}")

    fig1.suptitle('Livebox throughput', fontsize=12)
    axs[0].legend(loc='upper center', ncol=2)
    axs[0].grid()


    # Subplot total throughput
    label = "total_throughput"
    axs[1].scatter(x, total_throughput, color='black', label=f"{label}")
    axs[1].legend(loc='upper center')
    axs[1].grid()


    #plt.show()


def save_plots():
    fig_nums = plt.get_fignums()
    figs = [plt.figure(n) for n in fig_nums]
    for i, fig in enumerate(figs):
        if i == 0:
            file_name = f"traffic_station.png"
        elif i == 1:
            file_name = f"traffic_livebox.png"
        elif i == 2:
            file_name = f"station_vs_livebox.png"
        fig.savefig(file_name)


def generate_traffic_plots(station_file: str, livebox_file: str):
    """Plot traffic files"""
    print("RUNNING PROGRAM: Plot real traffic")

    # Genrate stations file
    generate_stations_plots(station_file=station_file)

    # Generate livebox plots
    generate_livebox_plots(livebox_file=livebox_file)

    # Save plots
    save_plots()

