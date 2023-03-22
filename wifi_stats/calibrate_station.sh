#!/bin/bash

source config/variables.env

# Print setup args
echo ------------------------------
echo CALIBRATION INFO
echo Station to calibrate: $STATION_TO_CALIBRATE
echo Logging config file: $LOGGING_CONFIG_FILE
echo ------------------------------

echo Running program: CALIBRATE STATION
python3 main.py -p initial_calibrate_stations -n $BOX_NAME -l $LIVEBOX_IP_ADDR -u $LIVEBOX_USER -pw $LIVEBOX_PASSWORD -lc $LOGGING_CONFIG_FILE -sm $STATION_TO_CALIBRATE
