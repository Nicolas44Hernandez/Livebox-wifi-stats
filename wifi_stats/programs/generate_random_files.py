"""
Generate random files from that could be send to the connected stations
"""

import os
import logging

logger = logging.getLogger(__name__)

FILE_NAME = "random_file"

# 1 Station
FILES_1_STATION = [
    2500000,
    5000000,
    7500000,
    10000000,
    12500000,
    15000000,
    17500000,
    20000000,
    22500000,
    25000000,
    27500000,
    30000000,
    32500000,
    35000000,
    37500000,
    40000000,
    42500000,
    45000000,
    47500000,
    50000000,
    52500000,
    55000000,
    57500000,
    60000000,
    62500000,
    65000000,
    67500000,
    70000000,
    72500000,
    75000000,
    77500000,
    80000000,
    82500000,
    85000000,
    87500000,
    90000000,
    92500000,
    95000000,
    97500000,
    100000000,
]

# 2 Stations
FILES_2_STATION = [
    1250000,
    2500000,
    3750000,
    5000000,
    6250000,
    7500000,
    8750000,
    10000000,
    11250000,
    12500000,
    13750000,
    15000000,
    16250000,
    17500000,
    18750000,
    20000000,
    21250000,
    22500000,
    23750000,
    25000000,
    26250000,
    27500000,
    28750000,
    30000000,
    31250000,
    32500000,
    33750000,
    35000000,
    36250000,
    37500000,
    38750000,
    40000000,
    41250000,
    42500000,
    43750000,
    45000000,
    46250000,
    47500000,
    48750000,
    50000000,
]

# 3 Stations
FILES_3_STATION = [
    833333,
    1666666,
    2500000,
    3333333,
    4166666,
    5000000,
    5833333,
    6666666,
    7500000,
    8333333,
    9166666,
    10000000,
    10833333,
    11666666,
    12500000,
    13333333,
    14166666,
    15000000,
    15833333,
    16666666,
    17500000,
    18333333,
    19166666,
    20000000,
    20833333,
    21666666,
    22500000,
    23333333,
    24166666,
    25000000,
    25833333,
    26666666,
    27500000,
    28333333,
    29166666,
    30000000,
    30833333,
    31666666,
    32500000,
    33333333,
]

# 4 Stations
FILES_4_STATION = [
    625000,
    1250000,
    1875000,
    2500000,
    3125000,
    3750000,
    4375000,
    5000000,
    5625000,
    6250000,
    6875000,
    7500000,
    8125000,
    8750000,
    9375000,
    10000000,
    10625000,
    11250000,
    11875000,
    12500000,
    13125000,
    13750000,
    14375000,
    15000000,
    15625000,
    16250000,
    16875000,
    17500000,
    18125000,
    18750000,
    19375000,
    20000000,
    20625000,
    21250000,
    21875000,
    22500000,
    23125000,
    23750000,
    24375000,
    25000000,
]

FILES_TO_GENERATE = {
    1: FILES_1_STATION,
    2: FILES_2_STATION,
    3: FILES_3_STATION,
    4: FILES_4_STATION,
}

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

def run_generate_random_files(files_path: str, stations: int):
    """Entry point for generate random files program"""

    logger.info(f'RUNNING PROGRAM: generate random files for {stations} stations')

    for i, size in enumerate(FILES_TO_GENERATE[stations]):
        filename = f"{files_path}/{FILE_NAME}{i + 1}.txt"
        generate_big_random_bin_file(filename, size)
        logger.info(f"file: {filename} size: {size}B  created")


