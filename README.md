# irradiationDAQ for CROCs

This is a program for CROC irradiation data collection (originally made for an irradiation at Sandia National Lab).

The program is written in python3 and uses the RD53BminiDAQ software to run scans. The output of running

```
python3 irradiationDAQ -h
```


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


This will run a list of scans provided by the user for each CROC (also list provided by user, each entry the name of a folder holding the configs for that CROC and a Results directory) at regular intervals as specified by the CRON style time information. The time information is a string of the form

    {minute} {hour} {day of month} {month} {day of week}

where each of these is an integer or a list of integers separated by commas.

There is a directory in irradiationDAQ/ for each CROC within which live the config files and 
directories tmp/ and Results/. tmp/ is used within the script for handling swapping configurations as
the irradiation goes on. In Results/, there is a folder for each scan type within which are folders with
naming scheme `{scan}_{number}` where the number is just a running index. Within these folders will be a config/
directory containing the configuration files used to run the scan, whatever the scan actually
outputs, and a textfile called `terminal_dump.txt` which contains the raw commandline output of the
scan.The timestamp for a given scan can be determined using the terminal dump text file.

If this is all being prepared for the first time, currently the CROC directories can be populated
by running

	$./init.sh CROC1 CROC2 ...

where CROC1, CROC2, etc., are the names of the CROCS for which directories will be created. They will
be populated with boilerplate configuration files.

Another utility included is clean.sh which deletes all the contents of the task directories (i.e.
the `{task}_{number}` directories and their contents) which has proven worthwile in testing.

Also included is a script `parse.py` for parsing the data into a few usable .csv files. It needs a bit of work now, but is fairly legible and really just compiles data from many scans while fixing a few typos in the output files.
