#!/bin/bash

declare -a LOG_FILES=("chanim_stats.log"
                      "files_transfer.log"
                      "generate_ramdom_files.log"
                      "info_stations.log"
                      "main.log"
                      "static_data.log"
                      "switch_band.log"
                      "telnet.log"
                      "antenas_tx_rx_stats.log"
                      )

source config/variables.env

ANALYSIS_TIMESTAMP=$(date +"%Y-%m-%d_%H-%M")

# Print analysis args
echo ------------------------------
echo ANALYSIS INFO
echo Analysis timestamp: $ANALYSIS_TIMESTAMP
echo Livebox address: $LIVEBOX_IP_ADDR
echo Box name: $BOX_NAME
echo Connected stations: $CONNECTED_STATIONS
echo Analysis duration: $ANALYSIS_DURATION_IN_MINUTES
echo Files transfer config file: $FILES_TRASNSFER_CONFIG
echo Smokeping config file: $SMOKEPING_CONFIG
echo Logging config file: $LOGGING_CONFIG_FILE
echo Connected stations results config file: $CONNECTED_STATIONS_RESULTS_CONFIG
echo Antenas stats results config file: $ANTENAS_RESULTS_CONFIG
echo USB results device: $USB_RESULTS_DEVICE
echo Switch 5GHz band: $SWITCH_5GHZ_BAND
echo 5GHZ band ON period: $WIFI_5GHZ_BAND_ON_PERIOD_IN_SECS
echo 5GHZ band OFF period: $WIFI_5GHZ_BAND_OFF_PERIOD_IN_SECS
echo Sampling period for info request: $SAMPLING_PERIOD_IN_SECS
echo ------------------------------

# Create results files
echo "Creating log files..."
mkdir analyses_results
mkdir logs
mkdir analyses_results/$BOX_NAME
mkdir analyses_results/$BOX_NAME/$ANALYSIS_TIMESTAMP
mkdir analyses_results/$BOX_NAME/$ANALYSIS_TIMESTAMP/logs
mkdir analyses_results/$BOX_NAME/$ANALYSIS_TIMESTAMP/config
mkdir analyses_results/$BOX_NAME/$ANALYSIS_TIMESTAMP/config/smokeping
mkdir analyses_results/$BOX_NAME/$ANALYSIS_TIMESTAMP/results
mkdir analyses_results/$BOX_NAME/$ANALYSIS_TIMESTAMP/results/analysis_results
mkdir analyses_results/$BOX_NAME/$ANALYSIS_TIMESTAMP/results/smokeping
mkdir analyses_results/$BOX_NAME/$ANALYSIS_TIMESTAMP/results/smokeping/rrd_files

for log_file in "${LOG_FILES[@]}"
do
    if ! test -f "logs/$log_file"; then
        touch "logs/$log_file"
    fi
done

# Configure and run smokeping
if [ "$CONNECTED_STATIONS" -gt 0 ]; then
    echo  Launching Smokeping service
    sudo systemctl stop apache2 smokeping
    sleep 2
    sudo rm -f /var/lib/smokeping/SmokePing_*
    sudo cp $SMOKEPING_CONFIG/Targets /etc/smokeping/config.d/Targets
    sudo cp $SMOKEPING_CONFIG/Database /etc/smokeping/config.d/Database
    sudo cp $SMOKEPING_CONFIG/Probes /etc/smokeping/config.d/Probes
    sudo systemctl restart apache2 smokeping
    sleep 2
    sudo chmod -R 777 /var/lib/smokeping
fi

echo  ------------------------------------------------
# Generate random files
if [ "$CONNECTED_STATIONS" -gt 0 ]; then
    echo Running program: GENERATE RANDOM FILES
    sudo rm -r -f $FILES_TO_SEND
    sleep 1
    mkdir $FILES_TO_SEND
    echo Files to send in: $FILES_TO_SEND
    python3 main.py -p generate_random_files -s $CONNECTED_STATIONS -f $FILES_TO_SEND -lc $LOGGING_CONFIG_FILE -rd $USB_RESULTS_DEVICE
    sudo chmod -R 777 $FILES_TO_SEND
fi

# Run analysis programs
echo  Running program: STATIC DATA
python3 main.py -p static_livebox_data -n $BOX_NAME -l $LIVEBOX_IP_ADDR -u $LIVEBOX_USER -pw $LIVEBOX_PASSWORD -lc $LOGGING_CONFIG_FILE -rd $USB_RESULTS_DEVICE -ts $ANALYSIS_TIMESTAMP &

echo  Running program: CHANIM STATS
python3 main.py -p chanim_stats -n $BOX_NAME -l $LIVEBOX_IP_ADDR -u $LIVEBOX_USER -pw $LIVEBOX_PASSWORD -d $ANALYSIS_DURATION_IN_MINUTES -lc $LOGGING_CONFIG_FILE -rd $USB_RESULTS_DEVICE -sp $SAMPLING_PERIOD_IN_SECS -ts $ANALYSIS_TIMESTAMP &

echo  Running program: ANTENAS STATS
python3 main.py -p antenas -n $BOX_NAME -l $LIVEBOX_IP_ADDR -u $LIVEBOX_USER -pw $LIVEBOX_PASSWORD -d $ANALYSIS_DURATION_IN_MINUTES -lc $LOGGING_CONFIG_FILE -rd $USB_RESULTS_DEVICE -sp $SAMPLING_PERIOD_IN_SECS -ac $ANTENAS_RESULTS_CONFIG -ts $ANALYSIS_TIMESTAMP &

if [ "$SWITCH_5GHZ_BAND" = true ]; then
    echo  Running program: SWITCH BAND 5GHz
    python3 main.py -p switch_5GHz -n $BOX_NAME -l $LIVEBOX_IP_ADDR -u $LIVEBOX_USER -pw $LIVEBOX_PASSWORD -d $ANALYSIS_DURATION_IN_MINUTES -on $WIFI_5GHZ_BAND_ON_PERIOD_IN_SECS -off $WIFI_5GHZ_BAND_OFF_PERIOD_IN_SECS -lc $LOGGING_CONFIG_FILE -rd $USB_RESULTS_DEVICE -ts $ANALYSIS_TIMESTAMP &

fi

if [ "$CONNECTED_STATIONS" -gt 0 ]; then
    echo  Running program: INFO STATIONS STATS
    python3 main.py -p stations -n $BOX_NAME -l $LIVEBOX_IP_ADDR -u $LIVEBOX_USER -pw $LIVEBOX_PASSWORD -d $ANALYSIS_DURATION_IN_MINUTES -lc $LOGGING_CONFIG_FILE -rd $USB_RESULTS_DEVICE -sp $SAMPLING_PERIOD_IN_SECS -sc $CONNECTED_STATIONS_RESULTS_CONFIG -ts $ANALYSIS_TIMESTAMP &

    echo  Running program: FILES TRANSFER
    python3 main.py -p files_transfer -fc $FILES_TRASNSFER_CONFIG  -d $ANALYSIS_DURATION_IN_MINUTES -lc $LOGGING_CONFIG_FILE -rd $USB_RESULTS_DEVICE &
fi

echo  ------------------------------------------------

# Schedule results and logs extraction
echo "Schedule Results and logs extraction"
RESULTS_EXTRACTION_TIME=`expr $ANALYSIS_DURATION_IN_MINUTES + 1`
SMOKEPING_RESULT_FILES=`ls /var/lib/smokeping/*.rrd`

# Move analysis config to results folder
if [ "$CONNECTED_STATIONS" -gt 0 ]; then
    cp $SMOKEPING_CONFIG/Targets analyses_results/$BOX_NAME/$ANALYSIS_TIMESTAMP/config/smokeping/Targets
    cp $SMOKEPING_CONFIG/Database analyses_results/$BOX_NAME/$ANALYSIS_TIMESTAMP/config/smokeping/Databse
    cp $SMOKEPING_CONFIG/Probes analyses_results/$BOX_NAME/$ANALYSIS_TIMESTAMP/config/smokeping/Probes
    cp $FILES_TRASNSFER_CONFIG analyses_results/$BOX_NAME/$ANALYSIS_TIMESTAMP/config/
fi
cp config/variables.env analyses_results/$BOX_NAME/$ANALYSIS_TIMESTAMP/config/

# Move logs to results folder
for log_file in logs
do
   echo "mv -f $log_file analyses_results/$BOX_NAME/$ANALYSIS_TIMESTAMP/" | at now +$RESULTS_EXTRACTION_TIME minutes
done

# Move smokeping results to results folder
if [ "$CONNECTED_STATIONS" -gt 0 ]; then
    echo "sudo systemctl stop apache2 smokeping" | at now +$RESULTS_EXTRACTION_TIME minutes
    for result_file in $SMOKEPING_RESULT_FILES
    do
        echo Schedule task to retrieve $result_file
        echo "mv -f $result_file analyses_results/$BOX_NAME/$ANALYSIS_TIMESTAMP/results/smokeping/rrd_files/" | at now +$RESULTS_EXTRACTION_TIME minutes
    done
fi
echo "sudo chmod -R 777 analyses_results" | at now +$RESULTS_EXTRACTION_TIME minutes
echo "rm -r -f $FILES_TO_SEND" | at now +$RESULTS_EXTRACTION_TIME minutes
