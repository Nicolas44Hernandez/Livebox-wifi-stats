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
echo Setup files transfer config directory $SETUP_FILES_TRASNSFER_CONFIG_DIR
echo ------------------------------

# Create setup log files
for log_file in "${LOG_FILES[@]}"
do
    if ! test -f "logs/$log_file"; then
        touch "logs/$log_file"
    fi
done

echo  ------------------------------------------------
# Generate random files
echo Running program: GENERATE RANDOM FILES
sudo rm -r -f $FILES_TO_SEND
sleep 1
mkdir -p $FILES_TO_SEND/st_1 $FILES_TO_SEND/st_2 $FILES_TO_SEND/st_3 $FILES_TO_SEND/st_4
echo Files to send in: $FILES_TO_SEND
python3 main.py -p generate_random_files -s 1 -f $FILES_TO_SEND/st_1 -lc $LOGGING_CONFIG_FILE
python3 main.py -p generate_random_files -s 2 -f $FILES_TO_SEND/st_2 -lc $LOGGING_CONFIG_FILE
python3 main.py -p generate_random_files -s 3 -f $FILES_TO_SEND/st_3 -lc $LOGGING_CONFIG_FILE
python3 main.py -p generate_random_files -s 4 -f $FILES_TO_SEND/st_4 -lc $LOGGING_CONFIG_FILE
sudo chmod -R 777 $FILES_TO_SEND

echo  ------------------------------------------------

# Send transfer files to connected stations

echo Transfering files to stations
python3 main.py -p initial_files_transfer_to_stations -fc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_1/stations.yml -lc $LOGGING_CONFIG_FILE
python3 main.py -p initial_files_transfer_to_stations -fc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_2/stations.yml -lc $LOGGING_CONFIG_FILE
python3 main.py -p initial_files_transfer_to_stations -fc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_3/stations.yml -lc $LOGGING_CONFIG_FILE
python3 main.py -p initial_files_transfer_to_stations -fc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_4/stations.yml -lc $LOGGING_CONFIG_FILE
echo  ------------------------------------------------

