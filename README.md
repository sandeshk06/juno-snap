# junosnap
**Juno-Snapy: Junos Device Snapshot Manager**

**Overview:** Juno-Snapy is a powerful snapshot utility designed specifically for managing Junos devices. Built on top of the **Junos JSNAPy framework**, it provides an efficient way to capture and compare device states during network maintenance windows. This utility automates the process of taking pre- and post-maintenance snapshots, ensuring a smooth and reliable way to analyze changes in network device configurations.

**Key Features:**

1. **IP Validation:** Ensures that the provided IP addresses are valid and reachable before proceeding with any operations.
2. **SSH Connection Validation:** Verifies the SSH connection to the network device, ensuring secure and successful communication.
3. **Dynamic Configuration:** Automatically generates a config.yaml file tailored to the specific network device, streamlining the setup process.
4. **Snapshot Management:** Takes pre- and post-maintenance snapshots based on the commands specified in the command.yaml file, allowing for easy comparison.
5. **Automated Comparison:** Compares the pre and post-snapshots and provides an overview of the changes, helping identify any issues or deviations during the maintenance window. [uses jsnapy snap-snap-diff approach ]

**Use Case:** Juno-Snapy is especially useful during network maintenance. By automating the snapshot process, it provides network engineers with a reliable tool to track and validate changes, ensuring the network's integrity before and after maintenance activities.


**prequisites** 

-  Python3.8 or later , with pip3 package manager
-  jsnapy utility installed
-  prior knowledge of  how to use jsnapy command line tool if we want to  write test cases  for command

**Juno-snap utility installation**
- git clone https://github.com/sandeshk06/juno-snap.git
- cd juno-snap
- sudo pip3 install git+https://github.com/Juniper/jsnapy.git
- check *https://www.juniper.net/documentation/us/en/software/junos-snapshot/snapshot-python/topics/task/junos-snapshot-administrator-in-python-installation.html* for installation and  os requirement
- sudo pip3 install -r requirements.text
- check /etc/jsnapy/jsnapy.cfg  and /etc/jsnapy/logging.yml exist after jsnapy installation
- check janapy  binary location using below command and update same in  config.ini file
- which  jsnapy
- create custom snapshot directory under /opt/jsnapy/snapshots/  or any other location and update location under /etc/jsnapy/jsnapy.cfg file for snapshot


### Some important files to be used by utility 

**1. config.ini**
This file will store configurations, including credentials and paths required for the utility to function. Below is a sample structure for config.ini:
  - username and password: Credentials for the network device.
  - snap_dir: The directory where snapshots will be stored. default is /etc/jsnapy/jsnapy.cfg
  - jsnapy_config_file: Path to the jsnapy configuration file.
  - jsnapy_logging_file: Path to the logging configuration file for jsnapy.
  - jsnapy_bin_file: Location of the jsnapy binary, typically found in the installed Python binaries directory.

**2. snap_config.yaml**
This YAML file will be automatically created in the current directory. It will typically include configuration details that the utility uses during its execution, such as device-specific settings

**3. command_config.yaml**
This file specifies the commands to run on the network device, which are used for taking pre- and post-maintenance snapshots.
Refer to the jsnapy documentation for how to write additional test cases.

**4. snapshot_status.db**
This is a database file that tracks the state of snapshots:
 -  0: Snapshot not taken.
 -  1: Snapshot taken.

This file is automatically updated by the utility when snapshots are taken.

### Workflow:
1. Configuration: Set up config.ini with the necessary paths and credentials along with update commands in command_config.yaml
2. Initial Setup: Run the utility,enter device IP address , upon successful ip validation,device connectivity with given credentials checked then it will create snap_config.yaml and executes
commands / testcases mentioned in command_config.yaml.
3. Snapshot Status Tracking: The utility checks snapshot_status.db to determine the current state of snapshots and updates it as snapshots are taken.

### Summary:
- **config.ini:** Stores user credentials and paths.
- **snap_config.yaml:** Auto-generated, stores current session configurations.
- **command_config.yaml:** Specifies commands for pre/post-maintenance snapshots.
- **snapshot_status.db:** Tracks snapshot status (0 for not taken, 1 for taken).

### Pre-snapshot
<img width="811" alt="Screenshot-pre-snap" src="https://github.com/user-attachments/assets/7a781e6e-157c-422d-a087-58cdb5cd69ec">

### Post-snapshot and diff
<img width="892" alt="Screenshot-post-snap-diff" src="https://github.com/user-attachments/assets/802b52f2-854f-478c-9da3-15eca3804bb5">



  

