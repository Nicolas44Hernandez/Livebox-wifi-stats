"""Generate traffic config program entry point"""

import logging
import os
from typing import Iterable
import yaml
import random
import numpy as np
from programs.files_transfer import get_test_params
from common.plots import generate_plots

logger = logging.getLogger(__name__)

def generate_throughput_candidates_list(
    number_of_elements: int,
    accel_factor: float,
):
    """Generate list of candidates for a station in a period"""
    list_of_values = [0,1]
    previous = 1
    for i in range(number_of_elements - 2):
        value = round(previous*accel_factor,1)
        list_of_values.append(value)
        previous = value
    return list_of_values


def generate_station_throughputs_sequence_for_period(
        list_of_candidates: Iterable[float],
        standar_deviation: float,
        sample_size: int = 20,
        total_number_of_elements: int = 1000,
    ):
    """
    Generate random list of throughputs for a station, the generated values
    depend on RNORM function using average value contained in the list and a StDev
    """
    full_list = []
    exponent_factor = 1.3

    while len(full_list) < total_number_of_elements:

        # Random position in the throughput list
        position = round(np.random.uniform()*(len(list_of_candidates)-1))

        # Adjust the std deviation to the throughput
        if list_of_candidates[position] > standar_deviation * 5:
            local_standar_deviation = list_of_candidates[position] / 5
        else:
            local_standar_deviation = standar_deviation

        # Format normal function args
        mean = list_of_candidates[position]
        sd = local_standar_deviation
        local_sample_size = round(sample_size/(((position+1)**exponent_factor)))

        # Generate new list
        samples = np.random.normal(loc=mean, scale=sd, size=local_sample_size)
        _list = [round(sample,1) for sample in samples]
        # Remove negative elements
        new_list = [abs(element) for element in _list]

        # Concatenate elements to list
        if len(new_list) + len(full_list) <= total_number_of_elements:
            full_list = full_list + new_list
        else:
            elements_to_concatenate = total_number_of_elements - len(full_list)
            full_list = full_list + new_list[:elements_to_concatenate]

    return full_list

def generate_station_triangular_throughputs_sequence_for_period(
        total_number_of_elements: int = 1000,
        step: int=1,
        upsize: int=5
    ):
    """
    Generate a triangular test list of throughputs for a station
    """
    full_list = []
    while len(full_list) < total_number_of_elements:
        # Generate new list
        new_list = []
        for n in range(upsize):
            new_list.append(n*step)

        # Concatenate elements to list
        if len(new_list) + len(full_list) <= total_number_of_elements:
            full_list = full_list + new_list
        else:
            elements_to_concatenate = total_number_of_elements - len(full_list)
            full_list = full_list + new_list[:elements_to_concatenate]

    return full_list


def generate_constant_throughputs_sequence_for_period(
        total_number_of_elements: int = 1000,
        value: float=1,
    ):
    """
    Generate a constant test list of throughputs for a station
    """
    full_list = []
    for n in range(total_number_of_elements):
            full_list.append(value)
    return full_list



def generate_random_throughputs_for_stations(
    number_of_files_to_send_per_period,
    periods,
    standar_deviation,
    sample_size,
    stations_dict,
):
    """Generate random throughputs for the analysis for each station"""

    # Prefill throughputs_dict array
    throughputs_dict = {}
    for station in stations_dict:
        throughputs_dict[station["name"]] = {"throughputs": [], "direction": []}

    # Array used to select the stations trafficking
    stations_array = [station["name"] for station in stations_dict]

    # Loop over periods
    for n in range(periods):

        for station in stations_array:
            # Generate random for accel factor
            accel_factor = 1.45+(np.random.uniform()*.2)
            throughput_candidates_for_period = generate_throughput_candidates_list(number_of_elements=12, accel_factor=accel_factor)

            throughput_for_station = generate_station_throughputs_sequence_for_period(
                list_of_candidates=throughput_candidates_for_period,
                standar_deviation=standar_deviation,
                sample_size=sample_size,
                total_number_of_elements=number_of_files_to_send_per_period
            )

            ############################### FOR TEST ###############################
            # throughput_for_station = generate_station_triangular_throughputs_sequence_for_period(
            #     total_number_of_elements=number_of_files_to_send_per_period,
            #     step=1,
            #     upsize=10,
            # )

            # throughput_for_station = generate_constant_throughputs_sequence_for_period(
            #     total_number_of_elements=number_of_files_to_send_per_period,
            #     value=2
            # )
            #########################################################################

            # Append throughput for period
            throughputs_dict[station]["throughputs"] += throughput_for_station

            # Add random traffic direction
            _transfert_directions = [random.choice(["uplink", "downlink"]) for i in range(number_of_files_to_send_per_period)]
            throughputs_dict[station]["direction"] += _transfert_directions

    return throughputs_dict

def generate_stations_traffic_config_file(traffic_config_file_name: str, throughputs_dict):
    """Generate stations traffic config yml file"""

    logger.info(f"Writting traffic config file in: {traffic_config_file_name}")
    config_to_write_dict = {}
    for station in throughputs_dict:
        config_for_station = []
        for throughput, direction in zip(throughputs_dict[station]["throughputs"], throughputs_dict[station]["direction"]):
            entry_dict = {"throughput_Mbs": float(throughput), "direction": direction}
            config_for_station.append(entry_dict)
        config_to_write_dict[station] = config_for_station

    # Write file
    with open(traffic_config_file_name, 'w') as file:
        yaml.dump(config_to_write_dict, file)


def log_analysis_configuration_generated(throughputs_dict):
    """Log the generated configuration"""
    logger.info(f"***************Generated configuration*********************")
    for station in throughputs_dict:
        throughputs = throughputs_dict[station]["throughputs"]
        logger.info(f"Station {station}")
        logger.info(f"Throughputs {throughputs}")
    logger.info(f"***********************************************************")


def run_generate_traffic_config(
    stations_config: str,
    number_of_files_to_send_per_period: int,
    number_of_periods: int,
    standard_deviation: float,
    sample_size: int,
    traffic_config_file_name: str,
    traffic_plot_file_name: str,
):
    """Entry point for generate traffic config program"""

    logger.info(f'RUNNING PROGRAM: generate traffic config')
    logger.info(f"Stations config file: {stations_config}")
    logger.info(f"Number of periods: {number_of_periods}")
    logger.info(f"Standard deviation: {standard_deviation}")
    logger.info(f"Sample size: {sample_size}")
    logger.info(
        f"Number of files to send per period: {number_of_files_to_send_per_period}")
    logger.info(f"Traffic config file name: {traffic_config_file_name}")

    stations_dict, files_path = get_test_params(config_file=stations_config)

    # Generate random throughput for stations dict
    throughputs_dict = generate_random_throughputs_for_stations(
        number_of_files_to_send_per_period,
        number_of_periods,
        standard_deviation,
        sample_size,
        stations_dict,
    )

    # Print the generated throughputs for stations
    generate_plots(
        throughputs_dict,
        number_of_files_to_send_per_period,
        number_of_periods,
        traffic_plot_file_name
    )

    # Generate stations traffic config file
    generate_stations_traffic_config_file(traffic_config_file_name, throughputs_dict)

    # Manage directory permisions
    command = f"chmod -R 777 {files_path}"
    os.system(command)

    # Log generated configuration
    log_analysis_configuration_generated(throughputs_dict)
