"""
Generate random files from that could be send to the connected stations
"""

import os
import logging
from pathlib import Path
import shutil
from programs.files_transfer import get_test_params

logger = logging.getLogger(__name__)

FILE_NAME = "random_file"


def generate_big_random_bin_file(filename, size):
    """
    generate big binary file with the specified size in bytes
    :param filename: the filename
    :param size: the size in bytes
    """

    with open('%s' % filename, 'wb') as fout:
        fout.write(os.urandom(size))
    logger.info(f"Random binary file with size %f generated in %s",
                size, filename)
    return


def run_generate_random_files(total_steps: int, seconds_per_step: int, config_file: str):
    """Entry point for generate random files program"""

    logger.info(f'RUNNING PROGRAM: generate random files ')
    logger.info(f"steps: {total_steps}")
    logger.info(f"seconds_per_step: {seconds_per_step}")
    logger.info(f"config_file: {config_file}")

    stations_dict, files_path = get_test_params(config_file=config_file)
    try:
        shutil.rmtree(files_path, ignore_errors=False, onerror=None)
    except FileNotFoundError:
        pass

    # Create directories
    for station in stations_dict:
        station_name = station["name"]
        dir_name = f"{files_path}/{station_name}"
        Path(dir_name).mkdir(parents=True, exist_ok=True)

    # Create files
    for station in stations_dict:
        station_name = station["name"]
        increment_per_step_in_Mbps = station["throughput_increment_in_kbps"] / 1000
        dir_name = f"{files_path}/{station_name}"

        logger.info(f"Creating files for station {station_name}")
        logger.info(f"Files will be created in {dir_name}")
        logger.info(f"Number of files: {total_steps}")
        logger.info(
            f"Traffic increment per step in Mbps: {increment_per_step_in_Mbps}")

        for i in range(1, total_steps+1):
            filename = f"{dir_name}/{FILE_NAME}{i}.txt"
            # calculate size
            throughput = i * increment_per_step_in_Mbps
            file_size_in_bytes = int(
                (throughput * seconds_per_step) * (1000000/8))
            generate_big_random_bin_file(filename, file_size_in_bytes)
            logger.info(
                f"file: {filename} size: {file_size_in_bytes}B  created")

    # Manage directory permisions
    command = f"chmod -R 777 {files_path}"
    os.system(command)
