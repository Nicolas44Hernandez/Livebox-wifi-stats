import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["figure.figsize"] = [12, 8]
plt.rcParams["figure.autolayout"] = True

STATIONS_COLOR = ['b-', 'g-', 'r-', 'y-', 'k-']


def generate_plots(
    throughputs_dict,
    number_of_files_to_send_per_period: int,
    number_of_periods: int,
    traffic_plot_file_name: str
):
    """Generate annalysis traffic plots """

    generate_total_throughputs(
        throughputs_dict,
        number_of_files_to_send_per_period,
        number_of_periods,
        traffic_plot_file_name
    )

    generate_ul_throughputs(
        throughputs_dict,
        number_of_files_to_send_per_period,
        number_of_periods,
        traffic_plot_file_name
    )

    generate_dl_throughputs(
        throughputs_dict,
        number_of_files_to_send_per_period,
        number_of_periods,
        traffic_plot_file_name
    )

    save_figures(traffic_plot_file_name)


def generate_total_throughputs(
    throughputs_dict,
    number_of_files_to_send_per_period: int,
    number_of_periods: int,
    traffic_plot_file_name: str,
):
    """Create plot of total generated throughputs"""

    fig1, axs = plt.subplots(2)

    arrays_len = number_of_files_to_send_per_period * number_of_periods
    x = range(0, arrays_len, 1)

    # Calculate total traffic
    total = np.zeros(arrays_len)
    for i, station_throughputs in enumerate(throughputs_dict):
        total = total + throughputs_dict[station_throughputs]["throughputs"]

    # Plot stations troughtput
    for i, station_throughputs in enumerate(throughputs_dict):
        label = station_throughputs.split("_")[0]
        axs[0].step(x, throughputs_dict[station_throughputs]["throughputs"],
                    STATIONS_COLOR[i], linewidth=1.0, label=f"{label}")

    fig1.suptitle('Total traffic UL + DL', fontsize=12)
    axs[0].legend(loc='upper center', fancybox=True,
                  ncol=len(throughputs_dict))
    axs[0].grid()

    # Subplot total
    axs[1].step(x, total, 'c-', linewidth=1.0, label=f"TOTAL")
    axs[1].legend(loc='upper center')
    axs[1].grid()

    # Plot period lines
    for i in range(number_of_periods):
        axs[0].axvline(x=i*number_of_files_to_send_per_period,
                       color='k', linestyle='--')
        axs[1].axvline(x=i*number_of_files_to_send_per_period,
                       color='k', linestyle='--')


def generate_ul_throughputs(
    throughputs_dict,
    number_of_files_to_send_per_period: int,
    number_of_periods: int,
    traffic_plot_file_name: str,
):
    """Create plot of ul generated throughputs"""

    fig2, axs = plt.subplots(2)

    arrays_len = number_of_files_to_send_per_period * number_of_periods
    x = range(0, arrays_len, 1)

    # Calculate UL and DL traffic
    ul_dict = {}
    for station in throughputs_dict:
        _station_ul_throughputs = []
        for throughput, direction in zip(throughputs_dict[station]["throughputs"], throughputs_dict[station]["direction"]):
            if direction == "uplink":
                _station_ul_throughputs.append(throughput)
            elif direction == "downlink":
                _station_ul_throughputs.append(0)

        ul_dict[station] = _station_ul_throughputs

    # Calculate total traffic
    total_ul = np.zeros(arrays_len)
    for station in throughputs_dict:
        total_ul = total_ul + ul_dict[station]

    # Plot stations ul troughtput
    for i, station in enumerate(ul_dict):
        label = station.split("_")[0]
        axs[0].step(x, ul_dict[station], STATIONS_COLOR[i],
                    linewidth=1.0, label=f"{label}")

    fig2.suptitle('UL traffic', fontsize=12)
    axs[0].legend(loc='upper center', bbox_to_anchor=(
        0.5, 1.2), fancybox=True, ncol=len(ul_dict))
    axs[0].grid()

    # Subplot total
    axs[1].step(x, total_ul, 'c-', linewidth=1.0, label=f"TOTAL")
    axs[1].legend(loc='upper center')
    axs[1].grid()

    # Plot period lines
    for i in range(number_of_periods):
        axs[0].axvline(x=i*number_of_files_to_send_per_period,
                       color='k', linestyle='--')
        axs[1].axvline(x=i*number_of_files_to_send_per_period,
                       color='k', linestyle='--')


def generate_dl_throughputs(
    throughputs_dict,
    number_of_files_to_send_per_period: int,
    number_of_periods: int,
    traffic_plot_file_name: str,
):
    """Create plot of dl generated throughputs"""

    fig3, axs = plt.subplots(2)

    arrays_len = number_of_files_to_send_per_period * number_of_periods
    x = range(0, arrays_len, 1)

    # Calculate DL traffic
    dl_dict = {}
    for station in throughputs_dict:
        _station_dl_throughputs = []
        for throughput, direction in zip(throughputs_dict[station]["throughputs"], throughputs_dict[station]["direction"]):
            if direction == "uplink":
                _station_dl_throughputs.append(0)
            elif direction == "downlink":
                _station_dl_throughputs.append(throughput)

        dl_dict[station] = _station_dl_throughputs

    # Calculate total traffic
    total_dl = np.zeros(arrays_len)
    for station in throughputs_dict:
        total_dl = total_dl + dl_dict[station]

    # Plot stations ul troughtput
    for i, station in enumerate(dl_dict):
        label = station.split("_")[0]
        axs[0].step(x, dl_dict[station], STATIONS_COLOR[i],
                    linewidth=1.0, label=f"{label}")

    fig3.suptitle('DL traffic', fontsize=12)
    axs[0].legend(loc='upper center', bbox_to_anchor=(
        0.5, 1.2), fancybox=True, ncol=len(dl_dict))
    axs[0].grid()

    # Subplot total
    axs[1].step(x, total_dl, 'c-', linewidth=1.0, label=f"TOTAL")
    axs[1].legend(loc='upper center')
    axs[1].grid()

    # Plot period lines
    for i in range(number_of_periods):
        axs[0].axvline(x=i*number_of_files_to_send_per_period,
                       color='k', linestyle='--')
        axs[1].axvline(x=i*number_of_files_to_send_per_period,
                       color='k', linestyle='--')


def save_figures(traffic_plot_file_name):
    fig_nums = plt.get_fignums()
    figs = [plt.figure(n) for n in fig_nums]
    for i, fig in enumerate(figs):
        if i == 0:
            file_name = f"{traffic_plot_file_name}_total.png"
        elif i == 1:
            file_name = f"{traffic_plot_file_name}_ul.png"
        elif i == 2:
            file_name = f"{traffic_plot_file_name}_dl.png"
        fig.savefig(file_name)
