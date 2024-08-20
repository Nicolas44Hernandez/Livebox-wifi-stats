#!/bin/bash

declare -a LOG_FILES=("setup/setup.log"
                      "main.log"
                      "static_data.log"
                      "files_transfer.log"
                      requested_traffic.log
                      "stations_stats.log"
                      "radio_stats.log"
                      )

source config/variables.env

ANALYSIS_TIMESTAMP=$(date +"%Y-%m-%d_%H-%M")
ANALYSIS_DIR=analyses_results/$BOX_NAME/$ANALYSIS_TIMESTAMP
RESULTS_DIR=$ANALYSIS_DIR/results/analysis_results

# Print analysis args
echo ------------------------------
echo ANALYSIS INFO
echo Analysis timestamp: $ANALYSIS_TIMESTAMP
echo Livebox address: $LIVEBOX_IP_ADDR
echo Box name: $BOX_NAME
echo Connected stations: $CONNECTED_STATIONS
echo Analysis duration: $ANALYSIS_DURATION_IN_MINUTES
echo Stations config file: $STATIONS_CONFIG
echo Traffic config file: $TRAFFIC_CONFIG
echo Smokeping config file: $SMOKEPING_CONFIG
echo Logging config file: $LOGGING_CONFIG_FILE
echo Connected stations results config file: $CONNECTED_STATIONS_RESULTS_CONFIG
echo Radio counters results config file: $RADIO_COUNTERS_RESULTS_CONFIG
echo USB results device: $USB_RESULTS_DEVICE
echo 5GHZ band ON period: $WIFI_5GHZ_BAND_ON_PERIOD_IN_SECS
echo 5GHZ band OFF period: $WIFI_5GHZ_BAND_OFF_PERIOD_IN_SECS
echo Sampling period for info request: $SAMPLING_PERIOD_IN_SECS
echo Analysis directory: $ANALYSIS_DIR
echo ------------------------------

# Create results files
echo "Creating log files..."
mkdir analyses_results
rm -r logs
mkdir logs
mkdir logs/setup
mkdir analyses_results/$BOX_NAME
mkdir $ANALYSIS_DIR
mkdir $ANALYSIS_DIR/logs
mkdir $ANALYSIS_DIR/config
mkdir $ANALYSIS_DIR/config/smokeping
mkdir $ANALYSIS_DIR/config/plots
mkdir $ANALYSIS_DIR/results
mkdir $ANALYSIS_DIR/results/analysis_results
mkdir $ANALYSIS_DIR/results/smokeping
mkdir $ANALYSIS_DIR/results/smokeping/rrd_files

for log_file in "${LOG_FILES[@]}"
do
    if ! test -f "logs/$log_file"; then
        touch "logs/$log_file"
    fi
done

# Configure and run smokeping
echo  Launching Smokeping service
sudo systemctl stop apache2 smokeping
sleep 2
sudo rm -f /usr/local/smokeping/data/SearchEngine/*.rrd
sudo cp $SMOKEPING_CONFIG /usr/local/smokeping/etc/config
sudo systemctl restart apache2 smokeping
echo ...
sleep 30
sudo chmod -R 777 /usr/local/smokeping/data/SearchEngine

echo  ------------------------------------------------
# Run analysis programs
echo  Running program: STATIC DATA
python3 main.py -p static_livebox_data -n $BOX_NAME -l $LIVEBOX_IP_ADDR -u $LIVEBOX_USER -pw $LIVEBOX_PASSWORD -lc $LOGGING_CONFIG_FILE -rf $RESULTS_DIR

echo  Running program: STATIONS STATS
python3 main.py -p stations -n $BOX_NAME -l $LIVEBOX_IP_ADDR -u $LIVEBOX_USER -pw $LIVEBOX_PASSWORD -d $ANALYSIS_DURATION_IN_MINUTES -lc $LOGGING_CONFIG_FILE -sp $SAMPLING_PERIOD_IN_SECS -sc $CONNECTED_STATIONS_RESULTS_CONFIG -rf $RESULTS_DIR &

echo  Running program: RADIO STATS
python3 main.py -p livebox_counters -n $BOX_NAME -l $LIVEBOX_IP_ADDR -u $LIVEBOX_USER -pw $LIVEBOX_PASSWORD -d $ANALYSIS_DURATION_IN_MINUTES -lc $LOGGING_CONFIG_FILE -sp $SAMPLING_PERIOD_IN_SECS -rc $RADIO_COUNTERS_RESULTS_CONFIG -rf $RESULTS_DIR &

echo  Running program: FILES TRANSFER
python3 main.py -p files_transfer -scf $STATIONS_CONFIG -tcf $TRAFFIC_CONFIG -td $TRANSFER_DURATION_IN_SECS -d $ANALYSIS_DURATION_IN_MINUTES -lc $LOGGING_CONFIG_FILE &

echo  ------------------------------------------------

# Move analysis config to results folder
cp $SMOKEPING_CONFIG $ANALYSIS_DIR/config/smokeping/
cp $STATIONS_CONFIG $ANALYSIS_DIR/config/
cp $TRAFFIC_CONFIG $ANALYSIS_DIR/config/
cp config/plots/* $ANALYSIS_DIR/config/plots

# Schedule results and logs extraction
echo "Schedule Results and logs extraction"
GENERATE_REQUESTED_TRAFFIC_FILE_TIME=`expr $ANALYSIS_DURATION_IN_MINUTES + 1`
RESULTS_EXTRACTION_TIME=`expr $ANALYSIS_DURATION_IN_MINUTES + 2`
SMOKEPING_RESULT_FILES=`ls /usr/local/smokeping/data/SearchEngine/*.rrd`

# Schedule move logs to results folder
for log_file in logs
do
   echo "mv -f $log_file $ANALYSIS_DIR/" | at now +$RESULTS_EXTRACTION_TIME minutes
done

Schedule generate requested throughput file
requested_traffic_result_file="$ANALYSIS_DIR/results/analysis_results"
traffic_log_file="logs/files_transfer.log"
antenas_log_file="logs/antenas_tx_rx_stats.log"
echo Schedule task to Generate result files $requested_traffic_result_file
echo "python3 results.py -tf $traffic_log_file -rd $requested_traffic_result_file -sc $STATIONS_CONFIG -lc $LOGGING_CONFIG_FILE" | at now +$GENERATE_REQUESTED_TRAFFIC_FILE_TIME minutes

# Move smokeping results to results folder
echo "sudo systemctl stop apache2 smokeping" | at now +$RESULTS_EXTRACTION_TIME minutes
for result_file in $SMOKEPING_RESULT_FILES
do
    echo Schedule task to retrieve $result_file
    echo "mv -f $result_file $ANALYSIS_DIR/results/smokeping/rrd_files/" | at now +$RESULTS_EXTRACTION_TIME minutes
done
echo "sudo chmod -R 777 analyses_results" | at now +$RESULTS_EXTRACTION_TIME minutes
