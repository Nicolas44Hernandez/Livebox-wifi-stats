"""
Generate random files from that could be send to the connected stations
"""

import os
import logging

logger = logging.getLogger(__name__)

FILE_NAME = "random_file"


def generate_big_random_bin_file(filename, size):
    """
    generate big binary file with the specified size in bytes
    :param filename: the filename
    :param size: the size in bytes
    """

    with open('%s' % filename, 'wb') as fout:
        fout.write(os.urandom(size))  # 1
    logger.info(f"Random binary file with size %f generated in %s",
                size, filename)
    return


def run_generate_random_files(files_path: str, stations: int, total_steps: int, seconds_per_step: int, trafic_increment_per_step_in_MB: int):
    """Entry point for generate random files program"""

    logger.info(f'RUNNING PROGRAM: generate random files ')
    logger.info(f"stations: {stations}")
    logger.info(f"steps: {total_steps}")
    logger.info(f"seconds_per_step: {seconds_per_step}")
    logger.info(
        f"trafic_increment_per_step_in_MB: {trafic_increment_per_step_in_MB}")

    # Create files
    for i in range(1, total_steps+1):
        filename = f"{files_path}/{FILE_NAME}{i}.txt"
        # calculate size
        throughput = i * trafic_increment_per_step_in_MB
        file_size_in_bytes = int(
            ((throughput/stations) * seconds_per_step) * (1000000/8))
        generate_big_random_bin_file(filename, file_size_in_bytes)
        logger.info(
            f"i: {i} t:{throughput} file: {filename} size: {file_size_in_bytes}B  created")
