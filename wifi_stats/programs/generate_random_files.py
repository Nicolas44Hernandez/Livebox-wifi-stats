"""
Generate random files from that could be send to the connected stations
"""

import os
import logging

logger = logging.getLogger(__name__)

FILE_NAME = "random_file"

FILES_SIZE_IN_BYTES = [
    3750000,
    6250000,
    8750000,
    11250000,
    13750000,
    16250000,
    18750000,
    21250000,
    23750000,
    26250000,
    28750000,
    31250000,
    33750000,
    36250000,
    38750000,
    41250000,
    43750000,
    46250000,
    48750000,
    51250000,
    53750000,
    56250000,
    58750000,
    61250000,
    63750000,
    66250000,
    68750000,
    71250000,
    73750000,
    76250000,
    78750000,
    81250000,
    83750000,
    86250000,
    88750000,
    91250000,
    93750000,
    96250000,
    98750000,
    101250000,
    103750000,
    106250000,
    108750000,
    111250000,
    113750000,
]

def generate_big_random_bin_file(filename,size):
    """
    generate big binary file with the specified size in bytes
    :param filename: the filename
    :param size: the size in bytes
    """

    with open('%s'%filename, 'wb') as fout:
        fout.write(os.urandom(size)) #1
    logger.info(f"Random binary file with size %f generated in %s", size, filename)
    return

def run_generate_random_files(files_path: str):
    """Entry point for generate random files program"""

    logger.info("RUNNING PROGRAM: generate random files")

    for i, size in enumerate(FILES_SIZE_IN_BYTES):
        filename = f"{files_path}/{FILE_NAME}{i + 1}.txt"
        generate_big_random_bin_file(filename, size)
        logger.info(f"file: {filename} size: {size}B  created")


