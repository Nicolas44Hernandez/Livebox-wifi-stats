import os
import logging

logger = logging.getLogger(__name__)

FILE_NAME = "random_file"
FILES_SIZE_IN_BYTES = [
    100000000,  # 100 MB
    200000000,  # 200 MB
    300000000,  # 300 MB
    400000000,  # 400 MB
    500000000,  # 500 MB
    600000000,  # 600 MB
]

def generate_big_random_bin_file(filename,size):
    """
    generate big binary file with the specified size in bytes
    :param filename: the filename
    :param size: the size in bytes
    """

    with open('%s'%filename, 'wb') as fout:
        fout.write(os.urandom(size)) #1
    logger.info(f"big random binary file with size %f generated in %s", size, filename)
    return

def run_generate_random_files(files_path: str):
    logger.info("RUNNING PROGRAM: generate random files")

    for i, size in enumerate(FILES_SIZE_IN_BYTES):
        filename = f"{files_path}/{FILE_NAME}{i}.txt"
        generate_big_random_bin_file(filename, size)
        logger.info(f"file: {filename} size: {size}B  created")


