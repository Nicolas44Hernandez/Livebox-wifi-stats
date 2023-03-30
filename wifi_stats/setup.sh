#!/bin/bash

declare -a LOG_FILES=("initial_files_transfer_to_stations.log"
                      "generate_ramdom_files.log"
                      "main.log"
                      )

source config/variables.env

# Print setup args
echo ------------------------------
echo SETUP INFO
echo Files transfer config file: $FILES_TRASNSFER_CONFIG
echo Logging config file: $LOGGING_CONFIG_FILE
echo Setup files transfer config directory: $SETUP_FILES_TRASNSFER_CONFIG_DIR
echo Number of files: $TOTAL_NUMBER_OF_FILES_TO_TRANSFER
echo Transfer duration: $TRANSFER_STEP_DURATION_IN_SECS
echo ------------------------------

# Create setup log files
mkdir logs
for log_file in "${LOG_FILES[@]}"
do
    if ! test -f "logs/$log_file"; then
        touch "logs/$log_file"
    fi
done

echo  ------------------------------------------------
# Generate random files
echo Running program: GENERATE RANDOM FILES
# python3 main.py -p generate_random_files -st $TOTAL_NUMBER_OF_FILES_TO_TRANSFER -sd $TRANSFER_STEP_DURATION_IN_SECS -fc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_1/stations.yml -lc $LOGGING_CONFIG_FILE
# python3 main.py -p generate_random_files -st $TOTAL_NUMBER_OF_FILES_TO_TRANSFER -sd $TRANSFER_STEP_DURATION_IN_SECS -fc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_2/stations.yml -lc $LOGGING_CONFIG_FILE
# python3 main.py -p generate_random_files -st $TOTAL_NUMBER_OF_FILES_TO_TRANSFER -sd $TRANSFER_STEP_DURATION_IN_SECS -fc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_3/stations.yml -lc $LOGGING_CONFIG_FILE
# python3 main.py -p generate_random_files -st $TOTAL_NUMBER_OF_FILES_TO_TRANSFER -sd $TRANSFER_STEP_DURATION_IN_SECS -fc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_4/stations.yml -lc $LOGGING_CONFIG_FILE
python3 main.py -p generate_random_files -st $TOTAL_NUMBER_OF_FILES_TO_TRANSFER -sd $TRANSFER_STEP_DURATION_IN_SECS -fc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_5/stations.yml -lc $LOGGING_CONFIG_FILE
echo  ------------------------------------------------

# Send transfer files to connected stations

echo Transfering files to stations
# python3 main.py -p initial_files_transfer_to_stations -fc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_1/stations.yml -lc $LOGGING_CONFIG_FILE
# python3 main.py -p initial_files_transfer_to_stations -fc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_2/stations.yml -lc $LOGGING_CONFIG_FILE
# python3 main.py -p initial_files_transfer_to_stations -fc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_3/stations.yml -lc $LOGGING_CONFIG_FILE
# python3 main.py -p initial_files_transfer_to_stations -fc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_4/stations.yml -lc $LOGGING_CONFIG_FILE
python3 main.py -p initial_files_transfer_to_stations -fc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_5/stations.yml -lc $LOGGING_CONFIG_FILE
echo  ------------------------------------------------

