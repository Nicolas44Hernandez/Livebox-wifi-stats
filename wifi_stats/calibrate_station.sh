#!/bin/bash


declare -a LOG_FILES=("initial_calibrate_stations.log"
                      "main.log"
                      )

source config/variables.env

# Create setup log files
mkdir logs
for log_file in "${LOG_FILES[@]}"
do
    if ! test -f "logs/$log_file"; then
        touch "logs/$log_file"
    fi
done

# Print setup args
echo ------------------------------
echo CALIBRATION INFO
echo Station to calibrate: $STATION_TO_CALIBRATE
echo Logging config file: $LOGGING_CONFIG_FILE
echo ------------------------------

echo Running program: CALIBRATE STATION
python3 main.py -p initial_calibrate_stations -n $BOX_NAME -l $LIVEBOX_IP_ADDR -u $LIVEBOX_USER -pw $LIVEBOX_PASSWORD -lc $LOGGING_CONFIG_FILE -sm $STATION_TO_CALIBRATE
