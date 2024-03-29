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
import argparse

 
#switch config to new tuning IN PROGRESS
def switch_config(croc, config_dir):
	subprocess.run(f"mv {base_dir}/*toml {base_dir}/tmp/; mv {base_dir}/*xml {base_dir}/tmp/", cwd=f'{base_dir}/{croc}', shell=True)
	subprocess.run("cp {config_dir}/* .", cwd=f'{croc}', shell=True)

#restore original config IN PROGRESS
def restore_config():
	print('in progress')

#Switch to a different config, storing the initial config in a tmp folder
def do_tasks():
    #loop over crocs
    for croc in crocs:
        #loop over tasks to be run
        for task in tasks:
            logger.info(f"Beginning {task}")
            i=1
            #manage the output directory names
            while os.path.exists(f'{base_dir}/{croc}/Results/{task}/{task}_{i}'):
                i+=1
            task_dir =f'{croc}/Results/{task}/{task}_{i}'
            #create the output directory
            os.mkdir(task_dir)

            #record time before starting task

            #with open etc. for writing the terminal dump, command must be run inside
            with open(f'{task_dir}/terminal_dump.txt', 'a') as f:
                if task in update_config_tasks:	
                        subprocess.run(f'RD53BminiDAQ -f CROC.xml -t RD53BTools.toml -o {task_dir[len(croc)+1:]} -s -h {task}', cwd=f'{base_dir}/{croc}', stdout=f, shell=True)
                        print("CHANGING CONFIGS!")
                else:
                        subprocess.run(f'RD53BminiDAQ -f CROC.xml -t RD53BTools.toml -o {task_dir[len(croc)+1:]} -h {task}', cwd=f'{base_dir}/{croc}', stdout=f, shell=True)

            #record time when task finishes
            logger.info(f"Finished {task}")

            #check if the task created its output: if it did, it passed, otherwise it failed (won't create output for failed scan)
            if os.path.exists(f'{base_dir}/{croc}/Results/{task}/{task}_{i}/{task}'):
                status = "pass"
                logger.info(f"{task} completed successfully")

                #cleanup/rearrange directories sensibly
                logger.debug("cleaning directories")
                subprocess.run(f"mv {base_dir}/{croc}/Results/{task}/{task}_{i}/{task}/* {base_dir}/{croc}/Results/{task}/{task}_{i}/", shell=True)
                subprocess.run(f"rm -rf {base_dir}/{croc}/Results/{task}/{task}_{i}/{task}", shell=True)
            else:
                status = "fail"
                logger.error(f"{task} failed")

#argument parser
parser = argparse.ArgumentParser(
        prog='python3 irradiationDAQ.py',
        description='CROC DAQ designed for use in irradiations',
        epilog='Created by Max Herrmann at CU Boulder'
)
parser.add_argument('-t', '--time', help='CRON style time information for when scans are to be run.', type=str, default='15,45 * * * *')
parser.add_argument('--crocs', nargs='+', help='List of CROCs to be used in the DAQ', type=str, default=['CROC_5D'])
parser.add_argument('--scans', nargs='+', help='List of scans to be run', type=str, default=['MuxScan', 'ShortRingOsc'])
args = parser.parse_args()


#set up logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stdout = colorlog.StreamHandler(stream=sys.stdout)
stdout.setLevel(logging.DEBUG)
fileout = logging.FileHandler("log.log")
fileout.setLevel(logging.DEBUG)

stdout_fmt = colorlog.ColoredFormatter("%(name)s: %(white)s%(asctime)s%(reset)s | %(log_color)s%(levelname)s%(reset)s | %(log_color)s%(message)s%(reset)s")
fileout_fmt = logging.Formatter("%(name)s: %(asctime)s | %(levelname)s | %(message)s")

stdout.setFormatter(stdout_fmt)
fileout.setFormatter(fileout_fmt)

logger.addHandler(stdout)
logger.addHandler(fileout)

# print to notify successful startup (soon should include restatement of which crocs, etc.) AND when the next spillshould be...
logger.setLevel(logging.DEBUG)

# define the base directory
# base_dir = '/home/hep/Test_CROC_SW/Ph2_ACF_24Dec22/MyDesktop/irradiationDAQ'
# base_dir = '/home/help/Test_CROC_SW/Ph2_ACF_CROC_20Sept22/MyDesktop/irradiationDAQ'
base_dir = '.'

#here we define a list of croc_names
#this should be read in from a text file the user prepares! ridiculous. should have the option, flags
#crocs = ["CROC_5D", "CROD_57"]
# crocs = ["CROC_5D"]
crocs = args.crocs


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
# tasks = ['ShortRingOsc', 'MuxScan', 'TempSensor', 'ShortRingOsc']
# silly naming convention
tasks = args.scans

#list of task names that will update the config
update_config_tasks = ['GlobalThresholdTuning', 'ThresholdEqualization']

#hopefully we can implement this later - for tracking which scans need to be run with multiple configs
multi_config_tasks = []
logger.info(f'Started normally! Running with "{args.time}" and for "{crocs}" with tasks "{tasks}"')
while True:
    try:
        now = datetime.datetime.now()
        cron = croniter.croniter(args.time, now)
        next_time = cron.get_next(datetime.datetime)
        logger.info('Next run at %s', next_time)
        time.sleep((next_time - now).seconds)
        do_tasks()
    except KeyboardInterrupt:
        logger.warning('Killed by user, exiting gracefully')
        exit(0)
