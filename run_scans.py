# Code for the January 2023 CROC irradiation at Sandia National Lab
# Max Herrmann CU Boulder January 2023
# maxwell.herrmann@colorado.edu
# (563)726-3086

import os
import sys
import time
import csv
import subprocess
import logging
import colorlog
import croniter
import datetime

#set up logging

logger = logging.getLogger("irradiationDAQ")

stdout = colorlog.StreamHandler(stream=sys.stdout)
fileout = logging.FileHandler("log.log")

stdout_fmt = colorlog.ColoredFormatter("%(name)s: %(white)s%(asctime)s%(reset)s | %(log_color)s%(levelname)s%(reset)s | %(log_color)s%(message)s%(reset)s")
fileout_fmt = logging.Formatter("%(name)s: %(asctime)s | %(levelname)s | %(message)s")

stdout.setFormatter(stdout_fmt)
fileout.setFormatter(fileout_fmt)

logger.addHandler(stdout)
logger.addHandler(fileout)

logging.basicConfig(
        filename='log.log', level=logging.DEBUG, 
        format=' %(levelname)s | %(asctime)s | %(message)s',
        datefmt='$Y-%m-%dT%H:%M:%SZ'
)

# print to notify successful startup (soon should include restatement of which crocs, etc.) AND when the next spillshould be...
logging.info('Started up normally!')

# define the base directory
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
tasks = ['ShortRingOsc', 'MuxScan', 'TempSensor', 'ShortRingOsc']

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
    #loop over crocs
    for croc in crocs:
        #loop over tasks to be run
        for task in tasks:
            logging.info(f"Beginning {task}")
            i=1
            #manage the output directory names
            while os.path.exists(f'{base_dir}/{croc}/Results/{task}/{task}_{i}'):
                i+=1
            task_dir =f'{base_dir}/{croc}/Results/{task}/{task}_{i}'
            #create the output directory
            os.mkdir(task_dir)

            #record time before starting task

            #with open etc. for writing the terminal dump, command must be run inside
            with open(f'{task_dir}/terminal_dump.txt', 'a') as f:
                if task in update_config_tasks:	
                        subprocess.run(f'RD53BminiDAQ -f CROC.xml -t RD53BTools.toml -o {task_dir[8:]} -s -h {task}', cwd=f'{base_dir}/{croc}', stdout=f, shell=True)
                        print("CHANGING CONFIGS!")
                else:
                        subprocess.run(f'RD53BminiDAQ -f CROC.xml -t RD53BTools.toml -o {task_dir[8:]} -h {task}', cwd=f'{base_dir}/{croc}', stdout=f, shell=True)

            #record time when task finishes
            logging.info(f"Finished {task}")

            #check if the task created its output: if it did, it passed, otherwise it failed (won't create output for failed scan)
            if os.path.exists(f'{base_dir}/{croc}/Results/{task}/{task}_{i}/{task}'):
                status = "pass"
                logging.info(f"{task} completed successfully")

                #cleanup/rearrange directories sensibly
                logging.debug("cleaning directories")
                subprocess.run(f"mv {base_dir}/{croc}/Results/{task}/{task}_{i}/{task}/* {base_dir}/{croc}/Results/{task}/{task}_{i}/", shell=True)
                subprocess.run(f"rm -rf {base_dir}/{croc}/Results/{task}/{task}_{i}/{task}", shell=True)
            else:
                status = "fail"
                logging.error(f"{task} failed")

now = datetime.datetime.now()
cron = croniter.croniter('15,45 * * * *', now)
while True:
    try:
        next_time = cron.get_next(datetime.datetime)
        time.sleep((next_time - now).seconds)
        do_tasks()
    except KeyboardInterrupt:
        logger.warning('Killed by user, exiting gracefully')
        exit(0)
