#!/bin/bash

declare -a LOG_FILES=("main.log"
                      files_transfer.log
                      )

source config/model_test_variables.env

# Print analysis args
echo ------------------------------
echo ANALYSIS INFO
echo Transfer duration: $TRANSFER_DURATION_IN_SECS
echo Analysis duration: $ANALYSIS_DURATION_IN_MINUTES
echo Stations config file: $STATIONS_CONFIG
echo Traffic config file: $TRAFFIC_CONFIG
echo Logging config file: $LOGGING_CONFIG_FILE
echo ------------------------------

# Create results files
echo "Creating log files..."
mkdir analyses_results
rm -r logs
mkdir logs

for log_file in "${LOG_FILES[@]}"
do
    if ! test -f "logs/$log_file"; then
        touch "logs/$log_file"
    fi
done

echo  ------------------------------------------------
# Run traffic for model test
echo  Running program: FILES TRANSFER
python3 main.py -p files_transfer -scf $STATIONS_CONFIG -tcf $TRAFFIC_CONFIG -td $TRANSFER_DURATION_IN_SECS -d $ANALYSIS_DURATION_IN_MINUTES -lc $LOGGING_CONFIG_FILE &

echo  ------------------------------------------------
