import os
import logging

logger = logging.getLogger(__name__)

FILE_NAME = "random_file"
FILES_SIZE_IN_BYTES = [
      5000000,  #   5 MB
     10000000,  #  10 MB
     50000000,  #  50 MB
     75000000,  #  75 MB
    100000000,  # 100 MB
    150000000,  # 150 MB
    200000000,  # 200 MB
    250000000,  # 250 MB
    300000000,  # 300 MB
    350000000,  # 350 MB
    400000000,  # 400 MB
    450000000,  # 450 MB
    500000000,  # 500 MB
    550000000,  # 550 MB
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
    logger.info(f"Random binary file with size %f generated in %s", size, filename)
    return

def run_generate_random_files(files_path: str):
    logger.info("RUNNING PROGRAM: generate random files")

    for i, size in enumerate(FILES_SIZE_IN_BYTES):
        filename = f"{files_path}/{FILE_NAME}{i}.txt"
        generate_big_random_bin_file(filename, size)
        logger.info(f"file: {filename} size: {size}B  created")


