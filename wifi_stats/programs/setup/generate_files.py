"""Generate files program entry point"""

import logging
import os
import yaml
from pathlib import Path
import shutil
from programs.files_transfer import get_test_params

FILE_NAME = "random_file"

logger = logging.getLogger(__name__)


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


def get_files_to_create_params(files_to_send_config_file: str):
    """Parse files to send config file"""
    logger.info(f"Files to send config file: {files_to_send_config_file}")
    # Read yml config file
    with open(files_to_send_config_file, "r") as stream:
        try:
            parsed_yaml = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error(exc)

    # Extract data
    return parsed_yaml["FILES_TO_TRANSFER"]


def run_generate_random_files(stations_config: str, files_to_send_config: str):
    """Entry point for generate random files program"""

    logger.info(f'RUNNING PROGRAM: generate random files ')
    logger.info(f"Stations config file: {stations_config}")
    logger.info(f"Files to send config file: {files_to_send_config}")

    stations_dict, files_path = get_test_params(config_file=stations_config)
    try:
        shutil.rmtree(files_path, ignore_errors=False, onerror=None)
    except FileNotFoundError:
        pass

    # Create directory
    Path(files_path).mkdir(parents=True, exist_ok=True)

    # Create files
    files_to_create_dict = get_files_to_create_params(files_to_send_config)
    for file in files_to_create_dict:
        throughput_MB = file["throughput_Mbs"]
        if throughput_MB == 0:
            continue
        filename = f"{files_path}/{FILE_NAME}_{throughput_MB}MB.txt"
        file_size_in_bytes = int(file["size_Mb"] * (1000000/8))
        generate_big_random_bin_file(filename, file_size_in_bytes)
        logger.info(
            f"file: {filename} size: {file_size_in_bytes}B  created")

    # Manage directory permisions
    command = f"chmod -R 777 {files_path}"
    os.system(command)
