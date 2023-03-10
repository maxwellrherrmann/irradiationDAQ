This is a program for data collection at the January 2023 CROC irradiation at Sandia National Lab.

For use (as it currently is) one need only run

	$python3 run_scans.py

This will run a list of scans currently maintained only inside the python script in a list called
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
