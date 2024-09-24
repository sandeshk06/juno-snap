# This file uses functionality from [junos-snapshot-administrator].
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
# http://www.apache.org/licenses/LICENSE-2.0
import subprocess
import sys
import os
import configparser
import time
from jinja2 import Template
import pickledb
import bcolors as b
import re
import locale
from netmiko import ConnectHandler, NetMikoTimeoutException, NetMikoAuthenticationException

os.environ["PYTHONIOENCODING"] = "utf-8"
scriptLocale=locale.setlocale(category=locale.LC_ALL, locale="en_US.UTF-8")

config=configparser.ConfigParser()
config.read("./config.ini")
db_file="./snapshot_status.db"


class JsnapyConf:

    def __init__(self,):
        self.network_user=config.get("NETWORK","username")
        self.network_password=config.get("NETWORK","password")
        self.snap_dir=config.get("UTILITY","snap_dir")
        self.jsnapy_config_file=config.get("UTILITY","jsnapy_config_file")
        self.jsnapy_logging_file=config.get("UTILITY","jsnapy_logging_file")
        self.jsnapy_bin_file=config.get("UTILITY","jsnapy_bin_file")
        self.snapshot_conf_yaml="./snap_config.yaml"
        self.command_conf_yaml="./command_config.yaml"

    def clenaup_invalid_files(self,invalid_file_list):
        for file_name in invalid_file_list:
            file_path=os.path.join(self.snap_dir,file_name)
            os.remove(file_path)

    def create_snapshot_dir(self,):
        os.makedirs(self.snap_dir) or print("{}[+] jsnapy snapshot dir path created successfully{}".format(b.OKMSG,b.END)) if not os.path.exists(self.snap_dir) else  print("{}[+] jsnapy snapshot dir path already present{}".format(b.OKMSG,b.END))


    def check_for_jsnapy_utility_config(self,):

        print("{}[-] jsnapy config file not exists | check documentation for jsnapy and create same under /etc/jsnapy/ dir{}".format(b.ERRMSG,b.END)) or sys.exit(2) if not os.path.isfile(self.jsnapy_config_file) else print("{}[+] jsnapy config file exists{}".format(b.OKMSG,b.END))

        print("{}[-] jsnapy logging file not exists | check documentation for jsnapy and create same under /etc/jsnapy/ dir{}".format(b.ERRMSG,b.END)) or sys.exit(2) if not os.path.isfile(self.jsnapy_logging_file) else print("{}[+] jsnapy logging file exists{}".format(b.OKMSG,b.END))

        print("{}[-] jsnapy bin file not exists | check documentation for jsnapy and  install jsnapy package using pip3 {}".format(b.ERRMSG,b.END)) or sys.exit(2) if not os.path.isfile(self.jsnapy_bin_file) else print("{}[+] jsnapy bin file exists{}".format(b.OKMSG,b.END))

    def pickle_db_file_creation(self,status_dir):
        try:

            db = pickledb.load(db_file, False,sig=False)
            for key, value in status_dir.items():
                db.set(key,value)
            db.dump()

        except Exception as err:
            print("{}[-]Exception occoured in gen_db_files function: {}{}".format(b.ERRMSG,err,b.END))
        except KeyboardInterrupt:
            print("{}[-] Keyboard Interrupt{}".format(b.ERRMSG,b.END))


    def create_yaml_config_file(self, device_list):
        try:
            tm = Template("""
---
hosts:
    {% for  device in device_list  -%}
    - device: {{ device }}
      username: "{{ network_username }}"
      passwd: "{{ network_password }}"
    {% endfor %}
tests:
    -  {{ command_config_file }}
            """)
            msg = tm.render(network_username=self.network_user,network_password=self.network_password,device_list=device_list,command_config_file=self.command_conf_yaml)
            print("{}[+] creating configuration file {}".format(b.OKMSG,b.END))
            with open(self.snapshot_conf_yaml,'w') as f:
                f.writelines(msg)
                print("{}[+] created config file successfully {}".format(b.OKMSG,b.END))


        except Exception as ErrMsg:
             print("{}[-] exception occoured while creating snapshot config yaml file:{}{}".format(b.ERRMSG,ErrMsg,b.END))
             sys.exit(2)
        except KeyboardInterrupt:
            print("{}[-] Keyboard Interrupt{}".format(b.ERRMSG,b.END))

    def check_device_connectivity(self,IP):
        try:

            junos_device = {

            'device_type': 'juniper',
            'ip': IP,
            'username': self.network_user,
            'password': self.network_password
            #'read_timeout' : 30
            }

            with  ConnectHandler(**junos_device) as net_connect:
                print("{}[+] Device connectivity successful{}".format(b.OKMSG,b.END))

        except NetMikoTimeoutException as errMsg:
            print("{}[-] Device timed out IP :{}: Error:{}{}".format(b.ERRMSG,IP,errMsg,b.END))
            sys.exit(2)
        except NetMikoAuthenticationException as errMsg:
            print("{}[-] Authentication failed IP:{}| Error :{}{}".format(b.ERRMSG,IP,errMsg,b.END))
            sys.exit(2)
        except Exception as errMsg:
            print("{}[-] Exception occoured error{}".format(b.OKMSG,IP,errMsg,b.END))
            sys.exit(2)
        except KeyboardInterrupt:
            print("{}[-] Keyboard Interrupt{}".format(b.ERRMSG,b.END))


    def call_jsnapy_utility(self,flag):
        try:
            subprocess.run([self.jsnapy_bin_file,'--snap',flag,'-f',self.snapshot_conf_yaml],check=True)

        except subprocess.CalledProcessError as e:
            print("{}[-] run_jsnapy_utility | Error occurred while executing command {}{}".format(b.ERRMSG,e,b.END))
            print("{}[-] Return code:{}{}".format(b.ERRMSG,e.returncode,b.END))
            sys.exit(2)
        except Exception as error:
            print("{}[-] Error run_jsnapy_utility | {}{}".format(b.ERRMSG,error,b.END))
            sys.exit(2)
        except KeyboardInterrupt:
            print("{}[-] Keyboard Interrupt{}".format(b.ERRMSG,b.END))

    def call_jsnapy_compare_utility(self):
        try:

            subprocess.run([self.jsnapy_bin_file,'--check','pre','post','-f',self.snapshot_conf_yaml],check=True)

        except subprocess.CalledProcessError as e:
            print("{}[-] run_jsnapy_compare_utility | Error occurred while executing command {}".format(b.ERRMSG,b.END))
            print("{}[-] Return code:{}{}".format(b.ERRMSG,e.returncode,b.END))
            sys.exit(2)
        except KeyboardInterrupt:
            print("{}[-] Keyboard Interrupt{}".format(b.ERRMSG,b.END))

    def dot_progress_bar(self,total, prefix='Backup Progress', suffix='Completed', length=30):
        for i in range(total):
            time.sleep(0.1)
            dots = '.' * ((i + 1) * length // total)
            sys.stdout.write(f'\r{b.OKMSG}{prefix}: [{dots:<{length}}] {suffix}{b.END}')
            sys.stdout.flush()
        print()

    def take_pre_snap(self,):
        try:
            status_dir={}
            if len(os.listdir(self.snap_dir)) == 0:
                print("{}[+] current snapshot dir {} is empty, No snapshot is present{}".format(b.OKMSG,self.snap_dir,b.END))
                status_dir={'pre':0,'post':0}
                self.pickle_db_file_creation(status_dir)
                #taking pre snpashot
                print("{}[+] taking pre snapshot{}".format(b.OKMSG,b.END))
                #function pre snpacall && db status update as pre=1
                self.call_jsnapy_utility('pre')
                self.dot_progress_bar(total=50)
                status_dir={'pre':1,'post':0}
                self.pickle_db_file_creation(status_dir)
                print("{}[+] pre snapshot taken successfully{}".format(b.OKMSG,b.END))
        except Exception as errMsg:
            print("{}[-] exception occoured while taking pre-snapshot for device:{}{}".format(b.ERRMSG,errMsg,b.END))
            sys.exit(2)
        except KeyboardInterrupt:
            print("{}[-] Keyboard Interrupt{}".format(b.ERRMSG,b.END))



    def take_post_snap(self,):
        try:
            status_dir={}
            print("{}[+] taking post snapshot{}".format(b.OKMSG,b.END))
            #function pre snpacall && db status update as pre=1
            self.call_jsnapy_utility(flag='post')
            self.dot_progress_bar(total=50)
            status_dir={'pre':1,'post':1}
            self.pickle_db_file_creation(status_dir)
            print("{}[+] post snapshot taken successfully{}".format(b.OKMSG,b.END))
        except Exception as errMsg:
            print("{}[-] exception occoured while taking pre-snapshot for device:{}{}".format(b.ERRMSG,errMsg,b.END))

    def current_db_status(self):
        status_dir={}
        try:
            db = pickledb.load(db_file, False,sig=False)
            for key in db.getall():
                status_dir[key] = db.get(key)
        except Exception as errMsg:
            print("{}[-] Error occoured while checking current db status for device:{}{}".format(b.ERRMSG,errMsg,b.END))
        except KeyboardInterrupt:
            print("{}[-] Keyboard Interrupt{}".format(b.ERRMSG,b.END))
        finally:
            return status_dir

    def Main(self,):
        try:

            #create snapshot dir if not exists
            self.create_snapshot_dir()
            #check for required configuration for jsnapy snapshot
            self.check_for_jsnapy_utility_config()

            if len(os.listdir(self.snap_dir)) != 0:
                print("{}[+] snapshotdir contains snapshots{}".format(b.OKMSG,b.END))
                #check for filename
                file_name_list=os.listdir(self.snap_dir)
                file_names="\n".join(file_name_list)
                print("{}[+] current snapshot present in folder :{}".format(b.OKMSG,b.END))
                print("{}{}{}".format(b.OKMSG,file_names,b.END))
                choice=input("{}[+] Do you want to proceed with current snapshot files? Enter [Y/N]{}".format(b.WARN,b.END))

                if choice =='' and choice not in ['Y','N','y','n']:
                    choice=("{}[-] Enter valid choice [Y/N]{}".format(b.ERRMSG,b.END))
                    sys.exit(2)

                if choice == 'Y' or choice == 'y':
                    pass
                    #proceed with further operations

                if choice == 'N' or choice == 'n':
                    #do cleanup of all current files present in snap_dir && update status in db
                    self.clenaup_invalid_files(file_name_list)
                    print("{}[+] cleaning up invalid files and taking fresh snapshot for device{}".format(b.ERRMSG,b.END))
                    status_dir={'pre':0,'post':0}
                    self.pickle_db_file_creation(status_dir)
                    self.take_pre_snap()
                    sys.exit(0)

                #checking status of snapshot dir whether  one snapshpt is taken
                #reading values from db file
                if os.path.isfile(db_file):
                    status_dir=self.current_db_status()
                    if status_dir['pre'] == 1:
                        print("{}[+] pre snapshot taken already for device{}".format(b.OKMSG,b.END))

                    if status_dir['post'] == 0:
                        self.take_post_snap()

                    status_dir=self.current_db_status()
                    if  status_dir['pre'] == 1 and  status_dir['post'] == 1:
                        #both snapshot taken already running comparision
                        print("{}[+] both pre and post activity snapshot are present{}".format(b.OKMSG,b.END))
                        self.call_jsnapy_compare_utility()
            else:
	            #take first snapshot
                self.take_pre_snap()

        except Exception as ErrMsg:
            print("{}[-] exception occoured in Main :{}{}".format(b.ERRMSG,ErrMsg,b.END))
        except KeyboardInterrupt:
            print("{}[-] Keyboard Interrupt{}".format(b.ERRMSG,b.END))

if __name__ == '__main__':
    try:
        msg="""

   d88b db    db d8b   db  .d88b.         .d8888. d8b   db  .d8b.  d8888b.
   `8P' 88    88 888o  88 .8P  Y8.        88'  YP 888o  88 d8' `8b 88  `8D
    88  88    88 88V8o 88 88    88        `8bo.   88V8o 88 88ooo88 88oodD'
    88  88    88 88 V8o88 88    88 C8888D   `Y8b. 88 V8o88 88~~~88 88~~~
db. 88  88b  d88 88  V888 `8b  d8'        db   8D 88  V888 88   88 88
Y8888P  ~Y8888P' VP   V8P  `Y88P'         `8888Y' VP   V8P YP   YP 88    version 0.1



        """
        print("{}{}{}".format(b.OKMSG,msg,b.END))
        device_ip=input("{}[+] Enter Device IP address for taking snapshot :{}".format(b.OKMSG,b.END))
        if device_ip =='':
            print("{}[-] IP address is blank{}".format(b.ERRMSG,b.END))
            sys.exit(2)
        regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
        if  not re.search(regex,device_ip):
            print("{}[-] IP address is not valid{}".format(b.ERRMSG,b.END))
            sys.exit(2)


        snap_config=JsnapyConf()
        snap_config.check_device_connectivity(device_ip)
        device_list=[]
        device_list.append(device_ip)
        snap_config.create_yaml_config_file(device_list)
        snap_config.Main()
    except KeyboardInterrupt:
        print("{}[-] Keyboard Interrupt{}".format(b.ERRMSG,b.END))
