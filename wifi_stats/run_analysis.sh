#!/bin/bash

declare -a LOG_FILES=("chanim_stats.log"
                      "files_transfer.log"
                      "generate_ramdom_files.log"
                      "info_stations.log"
                      "main.log"
                      "static_data.log"
                      "switch_band.log"
                      )

source config/variables.env

# Print args
echo ------------------------------
echo ANALYSIS INFO
echo Livebox address: $LIVEBOX_IP_ADDR
echo Box name: $BOX_NAME
echo Analysis duration: $ANALYSIS_DURATION_IN_MINUTES
echo Files transfer config file: $FILES_TRASNSFER_CONFIG
echo Logging config file: $LOGGING_CONFIG_FILE
echo Connected stations results config file: $CONNECTED_STATIONS_RESULTS_CONFIG
echo USB results device: $USB_RESULTS_DEVICE
echo 5GHZ band ON period: $WIFI_5GHZ_BAND_ON_PERIOD_IN_SECS
echo 5GHZ band OFF period: $WIFI_5GHZ_BAND_OFF_PERIOD_IN_SECS
echo Sampling period for info request: $SAMPLING_PERIOD_IN_SECS
echo ------------------------------

# Create log files
echo "Creating log files"
mkdir logs
for log_file in "${LOG_FILES[@]}"
do
    if ! test -f "logs/$log_file"; then
        touch "logs/$log_file"
    fi
done

# Run Analysis
echo ***** Running program: GENERATE RANDOM FILES
echo Files to send in: $FILES_TO_SEND
python3 main.py -p generate_random_files -f $FILES_TO_SEND -lc $LOGGING_CONFIG_FILE -rd $USB_RESULTS_DEVICE

echo ***** Running program: STATIC DATA
python3 main.py -p static_livebox_data -n $BOX_NAME -l $LIVEBOX_IP_ADDR -u $LIVEBOX_USER -pw $LIVEBOX_PASSWORD -lc $LOGGING_CONFIG_FILE -rd $USB_RESULTS_DEVICE &

echo ***** Running program: CHANIM STATS
python3 main.py -p chanim_stats -n $BOX_NAME -l $LIVEBOX_IP_ADDR -u $LIVEBOX_USER -pw $LIVEBOX_PASSWORD -d $ANALYSIS_DURATION_IN_MINUTES -lc $LOGGING_CONFIG_FILE -rd $USB_RESULTS_DEVICE -sp $SAMPLING_PERIOD_IN_SECS &

echo ***** Running program: INFO STATIONS STATS
python3 main.py -p stations -n $BOX_NAME -l $LIVEBOX_IP_ADDR -u $LIVEBOX_USER -pw $LIVEBOX_PASSWORD -d $ANALYSIS_DURATION_IN_MINUTES -lc $LOGGING_CONFIG_FILE -rd $USB_RESULTS_DEVICE -sp $SAMPLING_PERIOD_IN_SECS -sc $CONNECTED_STATIONS_RESULTS_CONFIG &

echo ***** Running program: SWITCH BAND 5GHz
python3 main.py -p switch_5GHz -n $BOX_NAME -l $LIVEBOX_IP_ADDR -u $LIVEBOX_USER -pw $LIVEBOX_PASSWORD -d $ANALYSIS_DURATION_IN_MINUTES -on $WIFI_5GHZ_BAND_ON_PERIOD_IN_SECS -off $WIFI_5GHZ_BAND_OFF_PERIOD_IN_SECS -lc $LOGGING_CONFIG_FILE -rd $USB_RESULTS_DEVICE &

echo ***** Running program: FILES TRANSFER
python3 main.py -p files_transfer -fc $FILES_TRASNSFER_CONFIG  -d $ANALYSIS_DURATION_IN_MINUTES -lc $LOGGING_CONFIG_FILE -rd $USB_RESULTS_DEVICE &
