import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["figure.figsize"] = [12, 8]
plt.rcParams["figure.autolayout"] = True

STATIONS_COLOR = ['blue', 'green', 'red', 'purple', 'black']
BINS=90


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
    )

    generate_ul_throughputs(
        throughputs_dict,
        number_of_files_to_send_per_period,
        number_of_periods,
    )

    generate_dl_throughputs(
        throughputs_dict,
        number_of_files_to_send_per_period,
        number_of_periods,
    )

    generate_stations_probability_distribution_function_plots(throughputs_dict)

    generate_stations_cumulative_probability_distribution_function_plots(
        throughputs_dict,
        number_of_files_to_send_per_period,
        number_of_periods
    )

    generate_total_distribution_plots(
        throughputs_dict,
        number_of_files_to_send_per_period,
        number_of_periods
    )

    save_figures(traffic_plot_file_name)


def generate_total_throughputs(
    throughputs_dict,
    number_of_files_to_send_per_period: int,
    number_of_periods: int,
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

def generate_stations_probability_distribution_function_plots(throughputs_dict):
    """Create plot of stations throughputs distributions"""

    if len(throughputs_dict.keys()) == 1:
        fig4, axs = plt.subplots()
    else:
        fig4, axs = plt.subplots(len(throughputs_dict.keys()))

    for i, station in enumerate(throughputs_dict):
        label = station.split("_")[0]

        # getting data of the histogram
        count, bins_count = np.histogram(throughputs_dict[station]["throughputs"], bins=BINS)

        # finding the PDF of the histogram using count values
        pdf = count / sum(count)

        # Plot PDF
        if len(throughputs_dict.keys()) == 1:
            axs.bar(
                bins_count[1:],
                pdf,
                width=3,
                color = STATIONS_COLOR[i],
                label=f"{label}",
            )
            axs.set_xticks(np.arange(0, max(throughputs_dict[station]["throughputs"])+1, 10), minor=False)
            axs.legend(loc='upper center')
            axs.grid()
        else:
            axs[i].bar(
                bins_count[1:],
                pdf,
                width=3,
                color = STATIONS_COLOR[i],
                label=f"{label}",
            )
            axs[i].set_xticks(np.arange(0, max(throughputs_dict[station]["throughputs"])+1, 10), minor=False)
            axs[i].legend(loc='upper center')
            axs[i].grid()


    fig4.suptitle('PDF by stations', fontsize=12)

def generate_stations_cumulative_probability_distribution_function_plots(
        throughputs_dict,
        number_of_files_to_send_per_period: int,
        number_of_periods: int
    ):
    """Create plot of stations throughputs probability distributions"""

    if len(throughputs_dict.keys()) == 1:
        fig5, axs = plt.subplots()
    else:
        fig5, axs = plt.subplots(len(throughputs_dict.keys()))

    for i, station in enumerate(throughputs_dict):
        label = station.split("_")[0]

        # initializing random values
        arrays_len = number_of_files_to_send_per_period * number_of_periods
        data = np.random.randn(arrays_len)
        data = throughputs_dict[station]["throughputs"]

        # getting data of the histogram
        count, bins_count = np.histogram(data, bins=BINS)

        # finding the PDF of the histogram using count values
        pdf = count / sum(count)
        # Generate CDF
        cdf = np.cumsum(pdf)

        # Plot CDF
        if len(throughputs_dict.keys()) == 1:
            axs.plot(
                bins_count[1:],
                cdf,
                color = STATIONS_COLOR[i],
                label=f"{label}"
            )
            axs.set_xticks(np.arange(0, max(bins_count)+1, 10), minor=False)
            axs.legend(loc='upper center')
            axs.grid()

        else:
            axs[i].plot(
                bins_count[1:],
                cdf,
                color = STATIONS_COLOR[i],
                label=f"{label}"
            )
            axs[i].set_xticks(np.arange(0, max(bins_count)+1, 10), minor=False)
            axs[i].legend(loc='upper center')
            axs[i].grid()

    fig5.suptitle('CDF function by stations', fontsize=12)



def generate_total_distribution_plots(
        throughputs_dict,
        number_of_files_to_send_per_period: int,
        number_of_periods: int):
    """Create plot of total throughputs distribution"""

    fig6, axs = plt.subplots(2)

    # Concatenate throughput arrays
    data = [0 for ele in range(number_of_files_to_send_per_period * number_of_periods)]
    for station in throughputs_dict:
        data = [ele + data[i] for i,ele in enumerate(throughputs_dict[station]["throughputs"])]

    # getting data of the histogram
    count, bins_count = np.histogram(data, bins=BINS)

    # finding the PDF of the histogram using count values
    pdf = count / sum(count)
    # Generate CDF
    cdf = np.cumsum(pdf)

    # Plot CDF
    axs[0].bar(
        bins_count[1:],
        pdf,
        width=3,
        color = "black",
        label=f"Probability distribution"
    )

    axs[0].set_xticks(np.arange(0, max(bins_count)+1, 10), minor=False)
    axs[0].legend(loc='upper center')
    axs[0].grid()

    # Plot CDF
    axs[1].plot(
        bins_count[1:],
        cdf,
        color = "black",
        label=f"Cumulative probability distribution"
    )

    axs[1].set_xticks(np.arange(0, max(bins_count)+1, 10), minor=False)
    axs[1].legend(loc='upper center')
    axs[1].grid()

    fig6.suptitle('Total PDF and CDF', fontsize=12)


def save_figures(traffic_plot_file_name):
    fig_nums = plt.get_fignums()
    figs = [plt.figure(n) for n in fig_nums]
    for i, fig in enumerate(figs):
        if i == 0:
            file_name = f"{traffic_plot_file_name}traffic_total.png"
        elif i == 1:
            file_name = f"{traffic_plot_file_name}traffic_ul.png"
        elif i == 2:
            file_name = f"{traffic_plot_file_name}traffic_dl.png"
        elif i == 3:
            file_name = f"{traffic_plot_file_name}probability_distribution_by_station.png"
        elif i == 4:
            file_name = f"{traffic_plot_file_name}cumulative_probability_distribution_by_station.png"
        elif i == 5:
            file_name = f"{traffic_plot_file_name}total_probability_distribution.png"
        fig.savefig(file_name)
