# Livebox-wifi-stats

This program aims to generate Wi-Fi statistics of the Livebox and the connected stations using the following programs:

| PROGRAM                 | FUNCTION                                                                            |
| ----------------------- | ----------------------------------------------------------------------------------- |
| Generate random files   | Generate long files with random data to send to stations as up trafic               |
| Initial files trasnfer  | Transfer files to connected stations, this will be used as down trafic              |
| Static data             | Write in a file static data from the livebox, master station and connected stations |
| Switch 5GHz band        | Activate and desactivate periodically the 5GHz WiFi band                            |
| Transfer files          | Transfer random files to connected stations                                         |
| Info connected stations | Get information of the stations connected to the WiFi network                       |
| Chanim stats            | Collect shanim stats from the Livebox WiFi bands                                    |
| Antenas stats           | Collect Tx and Rx stats from the Livebox WiFi bands                                 |

## SETUP

Required python version > 3.6

install PyYaml

```bash
sudo apt -y install python3-yaml
```

install sshpass

```bash
sudo apt-get install -y sshpass
```

install arp

```bash
sudo apt-get install -y net-tools
```

In addition, the following Python packages are required:

- PyYAML
- telnetlib3

## Configuration

Before launching the script it is necessary to configure the different input arguments of the different programs.
This can be done from the file `wifi_stats/config/variables.env`
| VARIABLE                          | WHAT IS?                                      | EXAMPLE                                                                 |
| --------------------------------- | --------------------------------------------- | ----------------------------------------------------------------------- |
| LIVEBOX_IP_ADDR                   | IP Address of the Livebox                     | 192.168.1.1                                                             |
| BOX_NAME                          | Name of the box (Only to results dir)         | liveboxNico                                                             |
| LIVEBOX_USER                      | Telnet user to connect to LB                  | root                                                                    |
| LIVEBOX_PASSWORD                  | Telnet password to connect to LB              | sah                                                                     |
| ANALYSIS_DURATION_IN_MINUTES      | Analysis total duration in minutes            | 60                                                                      |
| SWITCH_5GHZ_BAND                  | Activate switch band 5GHZ                     | true                                                                    |
| WIFI_5GHZ_BAND_ON_PERIOD_IN_SECS  | Time ON of the 5GHz band                      | 40                                                                      |
| WIFI_5GHZ_BAND_OFF_PERIOD_IN_SECS | Time OFF of the 5GHz band                     | 30                                                                      |
| SAMPLING_PERIOD_IN_SECS           | Results sample period                         | 4                                                                       |
| FILES_TO_SEND                     | Directory of the files to send to stations    | workspace/Livebox-wifi-stats/files_to_send                              |
| SETUP_FILES_TRASNSFER_CONFIG_DIR  | Files transfer configuration folder for setup | workspace/Livebox-wifi-stats/wifi_stats/config                          |
| FILES_TRASNSFER_CONFIG            | Files transfer configuration files            | workspace/Livebox-wifi-stats/wifi_stats/config/stations.yml             |
| LOGGING_CONFIG_FILE               | Logging configuration file                    | workspace/Livebox-wifi-stats/wifi_stats/config/logging.yml              |
| CONNECTED_STATIONS_RESULTS_CONFIG | Connected stations results config file        | workspace/Livebox-wifi-stats/wifi_stats/config/stations_info_config.yml |
| ANTENAS_RESULTS_CONFIG            | Antenas stats results config file             | workspace/Livebox-wifi-stats/wifi_stats/config/antenas_tx_rx_config.yml |
| USB_RESULTS_DEVICE                | USB drive to store the results in the livebox | dev-sda1                                                                |
| SMOKEPING_CONFIG                  | Smokeping configuration                       | workspace/Livebox-wifi-stats/wifi_stats/config/Targets                  |

### Files transfer configuration

Before launching the files transfer program, it is necessary to configure the transfer params for each station.
You can add a line in the file `wifi_stats/config/stations.env` to configure a file trasnfer to a station
For each station you need to add the following parameters
| VARIABLE      | WHAT IS?                                         | EXAMPLE      |
| ------------- | ------------------------------------------------ | ------------ |
| name          | Station name                                     | RPI          |
| ip            | station IP address                               | 192.168.1.13 |
| ssh_user      | station ssh user login necessary to scp transfer | nico         |
| ssh_password  | ssh user password necessary to scp transfer      | nico         |
| send_interval | time period in secs between each transfer        | 10           |
TODO: complete table

Transfer Configuration Example:

```yml
FILES_PATH: /home/nicolas/workspace/Livebox-wifi-stats/files_to_send/st_4/
STATIONS:
  - name: RPI 1
    ip: 192.168.1.25
    ssh_user: pc1_w
    ssh_password: Wigreen1234
    protocol: scp
    operative_system: Windows
    port: 22
    initial_data_rate_in_kbps: 0
    throughput_increment_in_kbps: 500
    initial_dead_time_in_secs: 10
    transfer_nb_per_step: 1
    send_interval_in_secs: 5
```


## RUN ANALYSIS SETUP

### RUN ANALYSIS

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
- initial_files_transfer_to_stations.log
- generate_ramdom_files.log
- info_stations.log
- main.log
- static_data.log
- switch_band.log
- antenas_tx_rx_stats.log
- telnet.log

## RESULTS FILES

The following result files are generated and saved to the usb drive:

- chanim_stats_2_4GHz.txt
- chanim_stats_5GHz.txt
- connections_number.txt
- info_station{n}.txt
- static_data.txt
- band_status_5GHz
- tx_rx_2g_stats.txt
- tx_rx_5g_stats.txt
