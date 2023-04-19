#!/bin/bash

declare -a LOG_FILES=("setup.log")

source config/variables.env

# Print setup args
echo ------------------------------
echo SETUP INFO
echo Files transfer config file: $FILES_TRASNSFER_CONFIG
echo Logging config file: $LOGGING_CONFIG_FILE
echo Setup files transfer config directory: $SETUP_FILES_TRASNSFER_CONFIG_DIR
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
python3 setup.py --generate-files -sc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations.yml -fc $SETUP_FILES_TRASNSFER_CONFIG_DIR/files_to_send_config.yml -sp $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_profiles_config.yml -nf '10' -p '10' -tc $SETUP_FILES_TRASNSFER_CONFIG_DIR/traffic_config_file.yml -ti $SETUP_FILES_TRASNSFER_CONFIG_DIR/analysis_traffic.png -lc $LOGGING_CONFIG_FILE
# python3 setup.py -sc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations.yml -fc $SETUP_FILES_TRASNSFER_CONFIG_DIR/files_to_send_config.yml -sp $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations_profiles_config.yml -nf '10' -p '10' -tc $SETUP_FILES_TRASNSFER_CONFIG_DIR/traffic_config_file.yml -ti $SETUP_FILES_TRASNSFER_CONFIG_DIR/analysis_traffic.png -lc $LOGGING_CONFIG_FILE
echo  ------------------------------------------------
