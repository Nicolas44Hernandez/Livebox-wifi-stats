# Livebox-wifi-stats

This program aims to generate Wi-Fi statistics of the Livebox and the connected stations using the following programs:

| PROGRAM                    | FUNCTION                                                                             |
| -------------------------- | ------------------------------------------------------------------------------------ |
| Generate random files      | Generate long files with random data to send to stations                             |
| Static data                | Write in a file static data from the livebox, master station and connected stations  |
| Switch 5GHz band           | Activate and desactivate periodically the 5GHz WiFi band                             |
| Transfer files             | Transfer random files to connected stations                                          |
| Info connected stations    | Get information of the stations connected to the WiFi network                        |
| Chanim stats               | Collect shanim stats from the Livebox WiFi bands                                     |

## SETUP

Required python version > 3.6

instal PyYaml

```bash
sudo apt -y install python-yaml
```

install sshpas

```bash
sudo apt-get install -y sshpass
```

## RUN ANALISIS

You can run the `run_analysis.sh` script to :

- Create the logs directory and files
- Run all the programs

### Analysis configuration

Before launching the script it is necessary to configure the different input arguments of the different programs.
This can be done from the file `wifi_stats/config/variables.env`
| VARIABLE  | WHAT IS?  | EXAMPLE |
| --------- | ------------ |------------ |
| LIVEBOX_IP_ADDR | IP Address of the Livebox | 192.168.1.1 |
| BOX_NAME | Name of the box (Only to results dir) | liveboxNico |
| LIVEBOX_USER | Telnet user to connect to LB | root |
| LIVEBOX_PASSWORD | Telnet password to connect to LB | sah |
| ANALYSIS_DURATION_IN_MINUTES | Analysis total duration in minutes | 60 |
| WIFI_5GHZ_BAND_ON_PERIOD_IN_SECS | Time ON of the 5GHz band | 40 |
| WIFI_5GHZ_BAND_OFF_PERIOD_IN_SECS | Time OFF of the 5GHz band | 30 |
| FILES_TO_SEND | Directory of the files to send to stations | workspace/Livebox-wifi-stats/files_to_send |
| FILES_TRASNSFER_CONFIG | Files transfer configuration files | workspace/Livebox-wifi-stats/wifi_stats/config/stations.yml |
| LOGGING_CONFIG_FILE | Logging configuration file | workspace/Livebox-wifi-stats/wifi_stats/config/logging.yml |
| USB_RESULTS_DEVICE | USB drive to store the results in the livebox | dev-sda1 |

### Files transfer configuration

Before launching the files transfer program, it is necessary to configure the transfer params for each station.
You can add a line in the file `wifi_stats/config/stations.env` to configure a file trasnfer to a station
For each station you need to add the following parameters
| VARIABLE  | WHAT IS?  | EXAMPLE |
| --------- | ------------ |------------ |
| name | Station name | RPI |
| ip | station IP address | 192.168.1.13 |
| ssh_user | station ssh user login necessary to scp transfer | nico |
| ssh_password | ssh user password necessary to scp transfer | nico |
| send_interval | time period in secs between each transfer | 10 |

Transfer Configuration Example:

```yml
FILES_PATH: /home/nicolas/workspace/Livebox-wifi-stats/files_to_send/
STATIONS:
  - name: RPI 1
    ip: 192.168.1.12
    ssh_user: nico
    ssh_password: nico
    send_interval: 30
  - name: RPI 2
    ip: 192.168.1.13
    ssh_user: nico
    ssh_password: nico
    send_interval: 30u
```

### RUN ALL THE PROGRAMS

```bash
chmod +x run_analysis.sh
```

Run the files:

``` bash
/.run_analysis.sh
```

### RUN SINGLE PROGRAM (VSCODE)

You can use the configurations from `.vscode/launch.json` to run and debug a single program
->  you need to manually create the logs files

## LOGS FILES

Each program has its own log file, the directory and the files are automatically created when launching the `run_analysis.sh` script

Log files:

- chanim_stats.log
- files_transfer.log
- generate_ramdom_files.log
- info_stations.log
- main.log
- static_data.log
- switch_band.log

## RESULTS FILES

The following result files are generated and saved to the usb drive:

- chanim_stats_2_4GHz.txt
- chanim_stats_5GHz.txt
- connections_number.txt
- info_station{n}.txt
- static_data.txt
- band_status_5GHz

## TODO LIST

General:

- [X] README.md
- [ ] Functions doc
- [X] ADD timestamp to results directory
- [X] add instal PyYaml to readme
- [X] add install sshpas to readme file
- [ ] ADD methods doc
- [X] double check logs
- [X] Logs redirection fix
- [X] Add vscode config for single program running

Script Chanim stats:

- [ ] Add master station timestamp as new column
- [X] Manage main loop with absolut time

Script static data:

- [X] Add network interfaces in result file (ifconfig)
- [X] Add mac and IP addresses in result file (arp -a)
- [X] Add sections by station in results file
- [ ] Firmeware version livebox

Script info conected stations

- [ ] Show connection number results file as table
- [ ] Show single station info as a table
- [ ] One file by mac address
- [X] Manage main loop with absolut time
- [ ] Check error in stations result file

Script switch 5GHz

- [X] Add ON / Off period as config variable
- [X] Double check variables
