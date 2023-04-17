"""Generate traffic config program entry point"""

import logging
import os
import yaml
import random
import matplotlib.pyplot as plt
import numpy as np
from programs.files_transfer import get_test_params
from programs.setup.generate_files import get_files_to_create_params

logger = logging.getLogger(__name__)

STATIONS_COLOR = ['b-', 'g-', 'r-', 'y-', 'k-']


def get_stations_profiles_params(stations_profiles_config: str):
    """Parse stations profiles config file"""
    logger.info(f"Stations profiles config file: {stations_profiles_config}")
    # Read yml config file
    with open(stations_profiles_config, "r") as stream:
        try:
            parsed_yaml = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error(exc)

    # Extract data
    return parsed_yaml["PROFILES"]


def get_throughput_for_profiles(stations_profiles, throughputs_array):
    """Generate dict of throughput profiles"""
    throughput_for_profiles_dict = {}
    for profile in stations_profiles:
        throughputs_array_for_profile = []
        _from = int(profile["from"])
        _to = int(profile["to"])
        _step = profile["step"]
        if _step:
            throughputs_array_for_profile = [_from, _to]
        else:
            for throughput, _ in throughputs_array:
                if throughput >= _from and throughput <= _to:
                    throughputs_array_for_profile.append(throughput)
        throughput_for_profiles_dict[profile["name"]
                                     ] = throughputs_array_for_profile

    return throughput_for_profiles_dict


def validate_configuration(
    configurations_in_analysis,
    candidate_stations_profiles_for_period
):
    """Validate candidate configuration for analysis"""
    validated = True
    for configuration in configurations_in_analysis:
        # Check if have the same number of stations trafficking
        stations_trafficking = len(configuration["stations"])
        if stations_trafficking == len(candidate_stations_profiles_for_period):
            # Check if have the same stations trafficking
            same_stations = True
            for station in candidate_stations_profiles_for_period:
                if station not in configuration["stations"]:
                    same_stations = False
            # If not the same stations config ok
            if not same_stations:
                continue

            # Check if same profiles in config
            same_profiles = True
            for station in candidate_stations_profiles_for_period:
                if not candidate_stations_profiles_for_period[station] == configuration["stations"][station]:
                    same_profiles = False

            # If not the same stations, config ok
            if not same_profiles:
                continue

    return validated


def generate_random_throughputs_for_stations(
    number_of_files_to_send_per_period,
    periods,
    stations_dict,
    throughput_for_profiles_dict
):
    """Generate random throughputs for the analysis for each station"""

    # Prefill throughputs_dict array
    throughputs_dict = {}
    for station in stations_dict:
        throughputs_dict[station["name"]] = {
            "throughputs": [], "profiles": []}

    # Array used to select the stations trafficking
    stations_array = [station["name"] for station in stations_dict]

    configurations_in_analysis = []

    # Loop over periods
    for n in range(periods):

        configuration_validated = False

        while not configuration_validated:

            # Generate candidate for configuration
            # Get stations trafficking
            nb_of_stations_trafficking = random.randrange(
                1, len(stations_array) + 1)
            stations_trafficking_in_period = random.sample(
                stations_array, k=nb_of_stations_trafficking)

            # Get random profile for stations
            stations_profiles_for_period = {}
            for station in stations_dict:
                profile_for_period = random.choice(
                    list(throughput_for_profiles_dict.keys()))
                stations_profiles_for_period[station["name"]
                                             ] = profile_for_period

            configuration_validated = validate_configuration(
                configurations_in_analysis,
                stations_profiles_for_period,
            )

        # Add profiles to dict throughputs_dict
        for station in stations_dict:
            throughputs_dict[station["name"]]["profiles"].append(
                stations_profiles_for_period[station["name"]])

        # Append period configuration to control array
        period_configuration = {
            "stations": stations_profiles_for_period,
        }
        configurations_in_analysis.append(period_configuration)

        # Fill random throughput array for each station
        for i in range(number_of_files_to_send_per_period):
            for station in stations_dict:
                if station["name"] in stations_trafficking_in_period:
                    _throughput = random.choice(
                        throughput_for_profiles_dict[stations_profiles_for_period[station["name"]]])
                else:
                    _throughput = 0

                throughputs_dict[station["name"]
                                 ]["throughputs"].append(_throughput)

    return throughputs_dict


def generate_plot_of_generated_throughputs(
    throughputs_dict,
    number_of_files_to_send_per_period: int,
    number_of_periods: int,
    traffic_plot_file_name: str,
):
    """Create plot of generated throughputs"""

    fig, axs = plt.subplots(2)

    arrays_len = number_of_files_to_send_per_period * number_of_periods
    plt.style.use('_mpl-gallery')
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

    axs[0].legend(loc='upper center', bbox_to_anchor=(
        0.5, 1.2), fancybox=True, ncol=len(throughputs_dict))
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
    plt.savefig(traffic_plot_file_name)


def generate_stations_traffic_config_file(traffic_config_file_name: str, throughputs_dict, throughputs_array):
    """Generate stations traffic config yml file"""

    logger.info(f"Writting traffic config file in: {traffic_config_file_name}")
    config_to_write_dict = {}
    for station in throughputs_dict:
        config_for_station = []
        for throughput in throughputs_dict[station]["throughputs"]:
            entry_dict = {"througput_Mbs": throughput}
            for th, times in throughputs_array:
                if th == throughput:
                    entry_dict["times"] = times
                    break
            config_for_station.append(entry_dict)
        config_to_write_dict[station] = config_for_station

    # Write file
    with open(traffic_config_file_name, 'w') as file:
        yaml.dump(config_to_write_dict, file)


def log_analysis_configuration_generated(throughputs_dict):
    """Log the generated configuration"""
    logger.info(f"***************Generated configuration*********************")
    for station in throughputs_dict:
        profiles = throughputs_dict[station]["profiles"]
        throughputs = throughputs_dict[station]["throughputs"]
        logger.info(f"Station {station}")
        logger.info(f"Profiles {profiles}")
        logger.info(f"Throughputs {throughputs}")
    logger.info(f"***********************************************************")


def run_generate_traffic_config(
    stations_config: str,
    files_to_send_config: str,
    stations_profiles_config: str,
    number_of_files_to_send_per_period: int,
    number_of_periods: int,
    traffic_config_file_name: str,
    traffic_plot_file_name: str,
):
    """Entry point for generate traffic config program"""

    logger.info(f'RUNNING PROGRAM: generate traffic config')
    logger.info(f"Stations config file: {stations_config}")
    logger.info(f"Files to send config file: {files_to_send_config}")
    logger.info(f"Stations profiles config file: {stations_profiles_config}")
    logger.info(f"Number of periods: {number_of_periods}")
    logger.info(
        f"Number of files to send per period: {number_of_files_to_send_per_period}")
    logger.info(f"Traffic config file name: {traffic_config_file_name}")

    stations_dict, files_path = get_test_params(config_file=stations_config)

    # Create throughput array
    files = get_files_to_create_params(files_to_send_config)
    throughputs_array = []
    for file in files:
        _data = (file["throughput_Mbs"], file["times_to_send"])
        throughputs_array.append(_data)

    # Load stations profiles config
    stations_profiles = get_stations_profiles_params(stations_profiles_config)
    throughput_for_profiles_dict = get_throughput_for_profiles(
        stations_profiles, throughputs_array)

    # Generate random throughput for stations dict
    throughputs_dict = generate_random_throughputs_for_stations(
        number_of_files_to_send_per_period,
        number_of_periods,
        stations_dict,
        throughput_for_profiles_dict
    )

    # Print the generated throughputs for stations
    generate_plot_of_generated_throughputs(
        throughputs_dict,
        number_of_files_to_send_per_period,
        number_of_periods,
        traffic_plot_file_name
    )

    # Generate stations traffic config file
    generate_stations_traffic_config_file(
        traffic_config_file_name, throughputs_dict, throughputs_array)

    # Manage directory permisions
    command = f"chmod -R 777 {files_path}"
    os.system(command)

    # Log generated configuration
    log_analysis_configuration_generated(throughputs_dict)
