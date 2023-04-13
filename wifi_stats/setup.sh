#!/bin/bash

declare -a LOG_FILES=("setup.log")

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
mkdir logs/setup
for log_file in "${LOG_FILES[@]}"
do
    if ! test -f "logs/setup/$log_file"; then
        touch "logs/setup/$log_file"
    fi
done

echo ---------------------SETUP-----------------------
#python3 setup.py --generate-files -sc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_3/stations.yml -fc $SETUP_FILES_TRASNSFER_CONFIG_DIR/files_to_send_config.yml -sp $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_profiles_config.yml -nf '20' -p '4' -s '2' -tc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_3/traffic_config_file.yml -ti $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_3/analysis_traffic.png -lc $LOGGING_CONFIG_FILE
python3 setup.py -sc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_3/stations.yml -fc $SETUP_FILES_TRASNSFER_CONFIG_DIR/files_to_send_config.yml -sp $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_profiles_config.yml -nf '20' -p '4' -s '2' -tc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_3/traffic_config_file.yml -ti $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_3/analysis_traffic.png -lc $LOGGING_CONFIG_FILE
python3 setup.py -sc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_2/stations.yml -fc $SETUP_FILES_TRASNSFER_CONFIG_DIR/files_to_send_config.yml -sp $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_profiles_config.yml -nf '20' -p '4' -s '1' -tc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_2/traffic_config_file.yml -ti $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_2/analysis_traffic.png -lc $LOGGING_CONFIG_FILE
python3 setup.py -sc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_1/stations.yml -fc $SETUP_FILES_TRASNSFER_CONFIG_DIR/files_to_send_config.yml -sp $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_profiles_config.yml -nf '20' -p '4' -s '1' -tc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_1/traffic_config_file.yml -ti $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_1/analysis_traffic.png -lc $LOGGING_CONFIG_FILE
# python3 setup.py -sc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_4/stations.yml -fc $SETUP_FILES_TRASNSFER_CONFIG_DIR/files_to_send_config.yml -sp $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_profiles_config.yml -nf '20' -p '4' -s '2' -tc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_4/traffic_config_file.yml -ti $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_4/analysis_traffic.png -lc $LOGGING_CONFIG_FILE
echo  ------------------------------------------------
