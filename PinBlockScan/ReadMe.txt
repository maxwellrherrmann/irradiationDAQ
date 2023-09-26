This program can read voltages from arduino, received data to calibrate the arduino, and setup the calibratio
of the arduino
Possible arguments(only one allowed at a time):
	-'python3 PinBlockScan.py tune file_path VSupply' will enter tuning where you can change the voltage across
the pins in use and the arduino will return the raw measurement value and put it in a csv file specified.
	-'python3 PinBlockScan.py setupPins' will allow you to choose the names of each of the pins on the arduino
and which ones to not use.
	-'python3 PinBlockScan.py setupCorrection' will display the current correction values to convert arduino
values to voltages and then ask the user to input the new calulated values.
	-'python3 PinBlockScan.py run [optional file_path] [optional VSupply]' will display the measured and 
calculated voltages from the arduino and put them into the specified file in csv format if file path is given.
If a file path is given an optional VSupply value can be added to add that value into the csv at the same 
time. The calculation of voltages is based on the correction values in the arduino setup with the setup 
command.
	-'python3 PinBlockScan.py periodicRun time_min csv_file_path' will collect the measured/calulated voltages
from the arduino and add them to the file at csv_file_path every time_min minutes")
	-'python3 PinBlockScan.py help' will display this menu.

