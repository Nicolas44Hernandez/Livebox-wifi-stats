"""Generate files program entry point"""

import logging
import os
from pathlib import Path
import shutil
from programs.files_transfer import get_test_params

FILE_NAME = "random_file"
FILE_SIZE_Mb = 3000

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

def run_generate_random_files(stations_config: str):
    """Entry point for generate random files program"""

    logger.info(f'RUNNING PROGRAM: generate random files ')
    logger.info(f"Stations config file: {stations_config}")

    stations_dict, files_path = get_test_params(config_file=stations_config)
    try:
        shutil.rmtree(files_path, ignore_errors=False, onerror=None)
    except FileNotFoundError:
        pass

    # Create directory
    Path(files_path).mkdir(parents=True, exist_ok=True)

    # Create file to send
    filename = f"{files_path}/{FILE_NAME}.txt"
    file_size_in_bytes = int(FILE_SIZE_Mb * (1000000/8))
    generate_big_random_bin_file(filename, file_size_in_bytes)
    logger.info(f"file: {filename} size: {file_size_in_bytes}B  created")

    # Manage directory permisions
    command = f"chmod -R 777 {files_path}"
    os.system(command)
