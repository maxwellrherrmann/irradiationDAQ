# Code for the January 2023 CROC irradiation at Sandia National Lab
# Max Herrmann CU Boulder January 2023
# maxwell.herrmann@colorado.edu
# (563)726-3086

import os
import csv
import subprocess
from datetime import datetime

#date formats for the filenames and the entries in the log file respectively
fmt = "%y_%m_%d-%H_%M_%S_%f"

base_dir = '/home/hep/Test_CROC_SW/Ph2_ACF_24Dec22/MyDesktop/irradiationDAQ'

#here we define a list of croc_names
#this should be read in from a text file the user prepares! ridiculous. should have the option, flags
#crocs = ["CROC_5D", "CROD_57"]
crocs = ["CROC_54"]

#need to fix the order of the scans, according to Luigi's schedule we have
#
#Threshold with initial config
#Threshold with latest tuned config
#tuning procedure to replace latest tuned config
#threshold scan with new tuned config
#noise scan
#ToT
#TimeWalk
#
#Stella's schedule must be slightly different, there are a few subtleties
"""
tasks =['ShortRingOsc', 'MuxScan', 'VrefTrimming', 'ChipBottomScans', 'Tuning', 'InTimeThreshold', 'ThresholdOscillation', 'ThresholdOscillationAsync', 'TimeWalk', 'TimeWalkAsync']
	}
#^ need to figure out what the output looks like of all these and if we really want them all. only two use change the config 
"""
#this list from Steve's old list
tasks = ['GlobalThresholdTuning', 'ThresholdEqualization', 'ThresholdScan', 'ShortRingOsc', 'MuxScan', 'TempSensor', 'ShortRingOsc']

#list of task names that will update the config
update_config_tasks = ['GlobalThresholdTuning', 'ThresholdEqualization']

#hopefully we can implement this later - for tracking which scans need to be run with multiple configs
multi_config_tasks = []
 
#switch config to new tuning IN PROGRESS
def switch_config(croc, config_dir):
	subprocess.run(f"mv {base_dir}/*toml {base_dir}/tmp/; mv {base_dir}/*xml {base_dir}/tmp/", cwd=f'{base_dir}/{croc}', shell=True)
	subprocess.run("cp {config_dir}/* .", cwd=f'{croc}', shell=True)

#restore original config IN PROGRESS
def restore_config():
	print('in progress')

#APPEND a new row to the log file
def write_log(name, croc, start_time, end_time, status, output_dir):
    with open('{base_dir}/log.csv', 'a') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow([name, croc, start_time, end_time, status, output_dir]) 

#Switch to a different config, storing the initial config in a tmp folder
def do_tasks():
    now = datetime.now().strftime(fmt)
    #loop over crocs
    for croc in crocs:
        #loop over tasks to be run
        for task in tasks:
            print(f"RUNNING {task}")
            i=1
            #manage the output directory names
            while os.path.exists(f'{base_dir}/{croc}/Results/{task}/{task}_{i}'):
                i+=1
            task_dir =f'{base_dir}/{croc}/Results/{task}/{task}_{i}'
            #create the output directory
            os.mkdir(task_dir)

            #record time before starting task
            start_time = datetime.now().strftime(fmt)

            #with open etc. for writing the terminal dump, command must be run inside
            with open(f'{task_dir}/terminal_dump.txt', 'a') as f:
                #writer = csv.writer(f, delimiter=',')
                if task in update_config_tasks:	
                        subprocess.run(f'RD53BminiDAQ -f CROC.xml -t RD53BTools.toml -o {task_dir[8:]} -s -h {task}', cwd=f'{base_dir}/{croc}', stdout=f, shell=True)
                        print("CHANGING CONFIGS!")
                else:
                        subprocess.run(f'RD53BminiDAQ -f CROC.xml -t RD53BTools.toml -o {task_dir[8:]} -h {task}', cwd=f'{base_dir}/{croc}', stdout=f, shell=True)

            #record time when task finishes
            end_time = datetime.now().strftime(fmt)
            print(f"FINISHING {task}") 

            #check if the task created its output: if it did, it passed, otherwise it failed (won't create output for failed scan)
            if os.path.exists(f'{base_dir}/{croc}/Results/{task}/{task}_{i}/{task}'):
                status = "pass"
                print(f"{task} PASS")

                #cleanup/rearrange directories sensibly
                print("CLEANING DIRECTORIES")
                subprocess.run(f"mv {base_dir}/{croc}/Results/{task}/{task}_{i}/{task}/* {base_dir}/{croc}/Results/{task}/{task}_{i}/", shell=True)
                subprocess.run(f"rm -rf {base_dir}/{croc}/Results/{task}/{task}_{i}/{task}", shell=True)
            else:
                status = "fail"
                print(f"{task} FAIL")

            #write to our general log file
            write_log(task, croc, start_time, end_time, status, f'{croc}/{task_dir}') 

do_tasks()
