#!/bin/bash

declare -a LOG_FILES=("setup.log")

source config/variables.env

# Print setup args
echo ------------------------------
echo SETUP INFO
echo Files transfer config file: $FILES_TRASNSFER_CONFIG
echo Logging config file: $LOGGING_CONFIG_FILE
echo Setup files transfer config directory: $SETUP_FILES_TRASNSFER_CONFIG_DIR
echo Total periods: $TOTAL_PERIODS
echo Files transfer per period: $FILES_TRANSFER_PER_PERIOD
echo Standard deviation: $STANDARD_DEVIATION
echo Sample size: $SAMPLE_SIZE
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
# python3 setup.py --generate-files -sc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations.yml -nf $FILES_TRANSFER_PER_PERIOD -p $TOTAL_PERIODS -sd $STANDARD_DEVIATION -ss $SAMPLE_SIZE -tc $SETUP_FILES_TRASNSFER_CONFIG_DIR/traffic_config_file.yml -ti $SETUP_FILES_TRASNSFER_CONFIG_DIR/plots/ -lc $LOGGING_CONFIG_FILE
python3 setup.py -sc $SETUP_FILES_TRASNSFER_CONFIG_DIR/stations.yml -nf $FILES_TRANSFER_PER_PERIOD -p $TOTAL_PERIODS -sd $STANDARD_DEVIATION -ss $SAMPLE_SIZE -tc $SETUP_FILES_TRASNSFER_CONFIG_DIR/traffic_config_file.yml -ti $SETUP_FILES_TRASNSFER_CONFIG_DIR/plots/ -lc $LOGGING_CONFIG_FILE
echo  ------------------------------------------------
