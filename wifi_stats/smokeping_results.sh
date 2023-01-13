#!/bin/bash
SMOKEPING_RESULT_FILES=`ls /var/lib/smokeping/*.rrd`

# Configure and run smokeping
echo  Launching Smokeping service
sudo systemctl stop apache2 smokeping
sleep 2
sudo rm -f /var/lib/smokeping/SmokePing_*
sudo systemctl restart apache2 smokeping
sleep 2
sudo chmod -R 777 /var/lib/smokeping


sleep 15

# Move smokeping results to results folder
#echo "sudo systemctl stop apache2 smokeping" | at now +$RESULTS_EXTRACTION_TIME minutes
sudo systemctl stop apache2 smokeping
for result_file in $SMOKEPING_RESULT_FILES
do
    mkdir test_results
    echo moving $result_file to test_results/
    mv -f $result_file test_results/
    # echo Schedule task to retrieve $result_file
    # echo "mv -f $result_file test_results/" | at now +1 minutes
done
