import random
import math
import numpy as np
import matplotlib.pyplot as plt

# Analysis configuration
NUMBER_OF_STATIONS = 3
MAX_NB_OF_STATIONS_TRAFFICKING = 2
SCENARIO_PERIOD = 4
NUMBER_OF_TX = 50

THROUGHPUTS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34,
               36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72, 74, 76, 78, 80]

FILES_SIZES = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 240, 280, 320, 360, 400, 240, 260, 280, 300, 320, 340, 360,
               380, 400, 400, 220, 220, 240, 240, 260, 260, 280, 280, 300, 300, 320, 320, 340, 340, 360, 360, 380, 380, 400, 400]

TIMES = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2,
         2, 2, 2, 2, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]

# Stations profiles
# SUPER_LOW      0 to 1 Mbps
# LOW            0 to 5 Mbps
# LOW_MEDIUM     0 to 24 Mbps
# MEDIUM         6 to 12 Mbps
# MEDIUM_HIGH    6 to 36 Mbps
# HIGH           14 to 36 Mbps
# SUPER_HIGH     38 to 60 Mbps
# ULTRA_HIGH     62 to 80 Mbps
# STEP           0 / 50 Mbps

SUPER_LOW = THROUGHPUTS[0:2]
LOW = THROUGHPUTS[0:math.ceil(len(THROUGHPUTS)/8)]
MEDIUM = THROUGHPUTS[math.ceil(len(THROUGHPUTS)/8):2*math.ceil(len(THROUGHPUTS)/8)]
LOW_MEDIUM = LOW+MEDIUM
HIGH = THROUGHPUTS[2*math.ceil(len(THROUGHPUTS)/8):4*math.ceil(len(THROUGHPUTS)/8)]
MEDIUM_HIGH = MEDIUM+HIGH
SUPER_HIGH = THROUGHPUTS[4 *
                         math.ceil(len(THROUGHPUTS)/8):6*math.ceil(len(THROUGHPUTS)/8)]
ULTRA_HIGH = THROUGHPUTS[6*math.ceil(len(THROUGHPUTS)/8):]
STEP = [THROUGHPUTS[0], THROUGHPUTS[5 * math.ceil(len(THROUGHPUTS)/8)]]


stations_trafficking_in_scenario = [0] * NUMBER_OF_STATIONS

throughputs = np.zeros((NUMBER_OF_STATIONS, SCENARIO_PERIOD*NUMBER_OF_TX))

STATIONS_NAMES = ["HUAWEI", "PC HP", "PC DELL", "GALAXY", "RASPBERRY"]
STATIONS_PROFILES = [SUPER_LOW, STEP, LOW, MEDIUM, MEDIUM_HIGH]
# STATIONS_PROFILES = [MEDIUM, MEDIUM, MEDIUM, MEDIUM, MEDIUM]
STATIONS_COLOR = ['b-', 'g-', 'y-', 'r-', 'k-']


stations_array = []
for st in range(NUMBER_OF_STATIONS):
    stations_array.append(st)

for n in range(SCENARIO_PERIOD):
    stations = random.sample(stations_array, k=MAX_NB_OF_STATIONS_TRAFFICKING)
    print(stations)
    for i in range(NUMBER_OF_TX):
        for station in stations:
            throughputs[station, int(
                (n * NUMBER_OF_TX) + i)] = random.choice(STATIONS_PROFILES[station])


fig, axs = plt.subplots(2)


for i, station_throughputs in enumerate(throughputs):
    print(f"Station {i} {station_throughputs}")

plt.style.use('_mpl-gallery')
x = range(0, NUMBER_OF_TX*SCENARIO_PERIOD, 1)

total = np.zeros(NUMBER_OF_TX*SCENARIO_PERIOD)
for i, station_throughputs in enumerate(throughputs):
    axs[0].step(x, station_throughputs,
                STATIONS_COLOR[i], linewidth=1.0, label=f"Station {i}")
    total = total + station_throughputs

# Subplot throughputs
axs[0].legend(loc='upper center')

# Subplot total
axs[1].step(x, total, 'c-', linewidth=1.0, label=f"TOTAL")
axs[1].legend(loc='upper center')

# plot periods

for i in range(SCENARIO_PERIOD):
    axs[0].axvline(x=i*NUMBER_OF_TX, color='k', linestyle='--')
    axs[1].axvline(x=i*NUMBER_OF_TX, color='k', linestyle='--')


plt.show()
