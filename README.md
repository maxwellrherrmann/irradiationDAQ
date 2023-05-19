# irradiationDAQ for CROCs

This is a program for CROC irradiation data collection (originally made for an irradiation at Sandia National Lab).

The program is written in python3 and uses the RD53BminiDAQ software to run scans. The output of running

$ python3 irradiationDAQ -h

```
usage: python3 irradiationDAQ.py [-h] [-t TIME] [--crocs CROCS [CROCS ...]] [--scans SCANS [SCANS ...]]

CROC DAQ designed for use in irradiations

options:
  -h, --help            show this help message and exit
  -t TIME, --time TIME  CRON style time information for when scans are to be run.
  --crocs CROCS [CROCS ...]
                        List of CROCs to be used in the DAQ
  --scans SCANS [SCANS ...]
                        List of scans to be run

Created by Max Herrmann at CU Boulder
```


This will run a list of scans provided by the user for each CROC (also list provided by user) at regular intervals as specified by the CRON style time information. The time information is a string of the form

    {minute} {hour} {day of month} {month} {day of week}

where each of these is an integer or a list of integers separated by commas.

'tasks' (here the names appear as they do when run with RD53BminiDAQ) for each CROC. In the main
program directory there live init.sh, run_scans.py, and log.csv. log.csv is a high-level log for
monitoring the status of scans as they are run. The format of the columns is

	task_name, croc, start_time, end_time, status, output_dir

There is a directory in irradiationDAQ/ for each CROC within which live the config files and 
directories tmp/ and Results/. tmp/ is used within the script for handling swapping configurations as
the irradiation goes on. In Results/, there is a folder for each scan within which are folders with 
naming scheme '{scan}_{number}' where the number is just a running index. The timestamp for a given
scan/folder can be determined by comparison with log.csv. Within these folders will be a config/
directory containing the configuration files used to run the scan, whatever the scan actually
outputs, and a textfile called terminal_dump.txt which contains the raw commandline output of the
scan.

If this is all being prepared for the first time, currently the CROC directories can be populated
by running

	$./init.sh CROC1 CROC2 ...

where CROC1, CROC2, etc., are the names of the CROCS for which directories will be created. I intend
to add functionality for a text file to be input instead. A similar system should be employed for
the scans to be performed (in progress).

Another utility included is clean.sh which deletes all the contents of the task directories (i.e.
the {task}_{number} directories and their contents) which has proven worthwile in testing.

Note: Currently (as of the evening of 1/4/2023) the .xml and .toml files for CROC_57 and CROC_5D
are configured for readout via the front of the Keithly; clearly in real operation one will be in
the rear, this remains to be chanegd, but it's unsure which will go where yet. In any event this
will be closely revisited tomorrow.
