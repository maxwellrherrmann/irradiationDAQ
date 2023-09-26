import serial
import time
import csv
from pathlib import Path
from serial.tools import list_ports
from datetime import datetime
import os
import pandas as pd
import sys
import select

def find_Arduinos(allowed_wait_time = 2):
	Possible_USB_Ports = []
	com_ports = list_ports.comports()
	for port in com_ports:
		man = port.manufacturer
		if(man != None and man.find("Arduino")>=0):
			Possible_USB_Ports.append(serial.Serial(port = port.device,baudrate=9600,timeout = allowed_wait_time))
	if(len(Possible_USB_Ports)==0):
		print("No possible Arduino USB ports found. Quiting program.")
		return("")
	else:
		time.sleep(allowed_wait_time)
		return(Possible_USB_Ports)


pin_names = ["A0:DEAD","A1:VINA","A2:VDDA","A3:VOFS","A4:VIND","A5:VDDD"]
	
def get_Data_Multiple_Arduinos(port_list, csv_file_path, VSupply = None, allowed_wait_time = 2):
	receivedHeaders = ""
	receivedData = ""
	for i in range(0,len(port_list)):
		print("Using device: %s" % (port_list[i].name))
		ser = port_list[i]
		totalWaitTime = 0
		ser.write(b'getDataHeaders')
		while(ser.in_waiting == 0 and totalWaitTime < allowed_wait_time):
			totalWaitTime += .1
			time.sleep(.1)
		receivedHeaders = receivedHeaders + (ser.readline().decode('ascii').strip())
		if(len(receivedHeaders) > 0):
			ser.write(b'measureVoltages10')
			totalWaitTime = 0
			while(ser.in_waiting == 0 and  totalWaitTime < allowed_wait_time):
				totalWaitTime += .1
				time.sleep(.1)
			if(ser.in_waiting > 0):
				receivedData = receivedData + (ser.readline().decode('ascii').strip())
			else:
				print("No Message Received")
				return(-1)
		else:
			print("No Headers Received")
			return(-1)
	if(VSupply == None):
		receivedHeaders = "Date Time (mm/dd/YYYY HH:MM:SS)" + receivedHeaders
		receivedData = datetime.now().strftime("%m/%d/%Y %H:%M:%S") + receivedData
	else:
		receivedHeaders = "Date Time (mm/dd/YYYY HH:MM:SS),VSupply" + receivedHeaders
		receivedData = datetime.now().strftime("%m/%d/%Y %H:%M:%S") + "," + str(VSupply) + receivedData
	if(csv_file_path == None):
		NewDataFrame = pd.DataFrame([receivedData.split(",")],columns=receivedHeaders.split(","))
		print("No data added to file(No csv_file_path passed)")
		print(NewDataFrame)
	else:
		File_Exists = Path(csv_file_path).is_file()
		if(File_Exists):
			NewDataFrame = pd.DataFrame([receivedData.split(",")],columns=receivedHeaders.split(","))
			print(NewDataFrame)
			DataFrame = pd.read_csv(csv_file_path,float_precision='round_trip')
			DataFrame = DataFrame.append(NewDataFrame,ignore_index=True)
			DataFrame.to_csv(csv_file_path,index=False)
		else:
			NewDataFrame = pd.DataFrame([receivedData.split(",")],columns=receivedHeaders.split(","))
			print(NewDataFrame)	
			with open(csv_file_path,'a', newline = '') as csvFile:
				csvWriter = csv.writer(csvFile, delimiter = ',')
				print("Creating new file")
				csvWriter.writerow(receivedHeaders.split(","))
				csvWriter.writerow(receivedData.split(","))

def getCorrection(port_list, allowed_wait_time = 2):
	ret = []
	for i in range(0,len(port_list)):
		print("Using device: %s" % (port_list[i].name))
		ser = port_list[i]
		totalWaitTime = 0
		ser.write(b'getCorrection')
		while(ser.in_waiting == 0 and totalWaitTime < allowed_wait_time):
			totalWaitTime += .1
			time.sleep(.1)
		if(ser.in_waiting > 0):
			ret.append(ser.readline().decode('ascii').strip())
		else:
			print("No responce")
			ret.append(False)
	return(ret)
			
def setCorrection(port_list,allowed_wait_time = 2):
	ret = []
	for i in range(0,len(port_list)):
		print("Using device: %s" % (port_list[i].name))
		ser = port_list[i]
		totalWaitTime = 0
		y_int = input("Input absolute value of y-int for MeasuredVal vs Voltage Graph:")
		slope = input("Input slope for MeasuredVal vs Voltage Graph:")
		message = "setCorrection" + slope + "," + y_int
		ser.write(message.encode('utf-8'))
		while(ser.in_waiting == 0 and totalWaitTime < allowed_wait_time):
			totalWaitTime += .1
			time.sleep(.1)
		if(ser.in_waiting > 0):
			print(ser.readline().decode('ascii').strip())
			ret.append(True)
		else:
			print("No responce for setCorrection")
			ret.append(False)
	return(ret)

def getPinNames(port_list, allowed_wait_time = 2):
	ret = []
	for i in range(0,len(port_list)):
		print("Using device: %s" % (port_list[i].name))
		ser = port_list[i]
		totalWaitTime = 0
		ser.write(b'getPinNames')
		while(ser.in_waiting == 0 and totalWaitTime < allowed_wait_time):
			totalWaitTime += .1
			time.sleep(.1)
		if(ser.in_waiting > 0):
			ret.append(ser.readline().decode('ascii').strip())
		else:
			print("No responce")
			ret.append(False)
	return(ret)
			
def setPinNames(port_list,allowed_wait_time = 2):
	ret = []
	for i in range(0,len(port_list)):
		print("Using device: %s" % (port_list[i].name))
		ser = port_list[i]
		totalWaitTime = 0
		ser.write(b'getNumPins')
		totalWaitTime = 0
		while(ser.in_waiting == 0 and totalWaitTime < allowed_wait_time):
			totalWaitTime += .1
			time.sleep(.1)
		if(ser.in_waiting > 0):
			num_pins = int(ser.readline().decode('ascii').strip())
			message = "setPinNames"
			for pin_num in range(0,num_pins):
				pinName = input("Input desired name of pin A%s(press enter to not use this pin):" % str(pin_num))
				message = message + "," + pinName
			totalWaitTime = 0
			ser.write(message.encode('utf-8'))
			while(ser.in_waiting == 0 and totalWaitTime < allowed_wait_time):
				totalWaitTime += .1
				time.sleep(.1)
			if(ser.in_waiting > 0):
				print(ser.readline().decode('ascii').strip())
				ret.append(True)
			else:
				print("No responce for setPinNames")
				ret.append(False)
		else:
			print("No Responce from Arduino")
	return(ret)

def tune(port_list,csv_file_path,VSupply,allowed_wait_time = 3):
	#input("What is the expected voltage accross the pins?(type anything besides numbers to exit):")
	receivedHeaders = ""
	receivedData = ""
	for i in range(0,len(port_list)):
		print("Using device: %s" % (port_list[i].name))
		ser = port_list[i]
		totalWaitTime = 0
		ser.write(b'getDataHeaders')
		while(ser.in_waiting == 0 and totalWaitTime < allowed_wait_time):
			totalWaitTime += .1
			time.sleep(.1)
		receivedHeaders = receivedHeaders + (ser.readline().decode('ascii').strip())
		if(len(receivedHeaders) > 0):
			ser.write(b'measureValues10')
			totalWaitTime = 0
			while(ser.in_waiting == 0 and  totalWaitTime < allowed_wait_time):
				totalWaitTime += .1
				time.sleep(.1)
			if(ser.in_waiting > 0):
				receivedData = receivedData + (ser.readline().decode('ascii').strip())
			else:
				print("No Message Received")
				return(-1)
		else:
			print("No Headers Received")
			return(-1)
	receivedHeaders = "Date Time (mm/dd/YYYY HH:MM:SS),VSupply" + receivedHeaders
	receivedData = datetime.now().strftime("%m/%d/%Y %H:%M:%S") + "," + str(VSupply)  + receivedData
	File_Exists = Path(csv_file_path).is_file()
	if(File_Exists):
		NewDataFrame = pd.DataFrame([receivedData.split(",")],columns=receivedHeaders.split(","))
		print(NewDataFrame)
		DataFrame = pd.read_csv(csv_file_path,float_precision='round_trip')
		DataFrame = DataFrame.append(NewDataFrame,ignore_index=True)
		DataFrame.to_csv(csv_file_path,index=False)
	else:
		print(receivedHeaders)
		print(receivedData)	
		with open(csv_file_path,'a', newline = '') as csvFile:
			csvWriter = csv.writer(csvFile, delimiter = ',')
			print("Creating new file")
			csvWriter.writerow(receivedHeaders.split(","))
			csvWriter.writerow(receivedData.split(","))
	
	


if(len(sys.argv) > 0):	
	if(sys.argv[1] == "setupCorrection"):
		ports = find_Arduinos()
		if(len(ports) == 0):
			print("No Arduinos found")
		else:
			cur_corrections = getCorrection(ports)
			for i in range(0,len(cur_corrections)):
				print("Current correction equation(%s):%s" % (ports[i].name, cur_corrections[i]))
			change_results = setCorrection(ports)
			for i in range(0,len(change_results)):
				if(change_results[i]):
					print("Correction updated(%s)" % ports[i].name)
				else:
					print("Failed to update correction(%s)" % ports[i].name)
			cur_corrections = getCorrection(ports)
			for i in range(0,len(cur_corrections)):
				print("Final correction equation(%s):%s" % (ports[i].name, cur_corrections[i]))
	elif(sys.argv[1] == "setupPins"):
		ports = find_Arduinos()
		if(len(ports) == 0):
			print("No Arduinos found")
		else:
			curPinNames = getPinNames(ports)
			for i in range(0,len(curPinNames)):
				print("Current pin names(%s):%s" % (ports[i].name, curPinNames[i]))
			change_results = setPinNames(ports)
			for i in range(0,len(change_results)):
				if(change_results[i]):
					print("Pin names updated(%s)" % ports[i].name)
				else:
					print("Failed to update pin name(%s)" % ports[i].name)
			curPinNames = getPinNames(ports)
			for i in range(0,len(curPinNames)):
				print("Final pin names(%s):%s" % (ports[i].name, curPinNames[i]))
 
	elif(sys.argv[1] == "periodicRun"):
		if(len(sys.argv) == 4):
			time_min = float(sys.argv[2])
			ports = find_Arduinos()
			if(len(ports)==0):
				print("No Arduino found")
			else:
				print("Reading Voltages")
				t_start = time.time()	
				get_Data_Multiple_Arduinos(port_list = ports,csv_file_path = sys.argv[3])
				num_digits = len(str(int(60*time_min)))
				num_runs = 0
				while(True):
					num_runs += 1
					next_run_time = t_start + num_runs*60*time_min
					print(str(int(60*time_min)) + " seconds till next run.('ctrl C' to stop)",end = '\r')	
					while(time.time() < next_run_time):
						time_left = next_run_time - time.time()
						for i in range(0,num_digits - len(str(int(time_left)))):
							print("0",end="")
						print(int(time_left),end = '\r')
					print("\nReading Voltages")
					get_Data_Multiple_Arduinos(port_list = ports,csv_file_path = sys.argv[3])
		else:
			print("periodicRun requires 2 arguments an amount of time in minutes and the file to store the data collected")
	elif(sys.argv[1] == "run"):
		if(len(sys.argv) == 2):
			ports = find_Arduinos()
			if(len(ports) == 0):
				print("No Arduino found")
			else:
				get_Data_Multiple_Arduinos(port_list = ports)
		elif(len(sys.argv) == 3):
			ports = find_Arduinos()
			if(len(ports)==0):
				print("No Arduino found")
			else:
				get_Data_Multiple_Arduinos(port_list = ports,csv_file_path = sys.argv[2])
		elif(len(sys.argv) == 4):
			ports = find_Arduinos()
			if(len(ports)==0):
				print("No Arduino found")
			else:
				get_Data_Multiple_Arduinos(port_list = ports,csv_file_path = sys.argv[2],VSupply = sys.argv[3])
		else:
			print("Must supply one file path for where to save the measured voltages and one optional VSupply")
	elif(sys.argv[1] == "tune"):
		if(len(sys.argv) == 4):
			ports = find_Arduinos()
			if(len(ports) == 0):
				print("No Arduino found")
			else:
				tune(ports,VSupply = sys.argv[3],csv_file_path = sys.argv[2])
		else:
			print("Must supply one file path for where to save the measured values and the voltage you are running at")
	elif(sys.argv[1] == "help"):
		print("This program can read voltages from arduino, received data to calibrate the arduino, and setup the calibration of the arduino")
		print("Possible arguments(only one allowed at a time):\n")
		print("'python3 PinBlockScan.py tune file_path VSupply' will enter tuning where you can change the voltage across the pins in use and the arduino will return the raw measurement value and put it in a csv file specified.\n")
		print("'python3 PinBlockScan.py setupPins' will allow you to choose the names of each of the pins on the arduino and which ones to not use.\n")
		print("'python3 PinBlockScan.py setupCorrection' will display the current correction values to convert arduino values to voltages and then ask the user to input the new calulated values.\n")
		print("'python3 PinBlockScan.py run [optional file_path] [optional VSupply]' will display the measured and calculated voltages from the arduino and put them into the specified file in csv format if file path is given. If a file path is given an optional VSupply value can be added to add that value into the csv at the same time. The calculation of voltages is based on the correction values in the arduino setup with the setup command.\n")
		print("'python3 PinBlockScan.py periodicRun time_min csv_file_path' will collect the measured/calulated voltages from the arduino and add them to the file at csv_file_path every time_min minutes")
		print("'python3 PinBlockScan.py help' will display this menu.\n")
	else:
		print("Argument not recognized. For help run 'python3 PinBlockScan.py help'")
else:
	print("Some arguments are required to run PinBlockScan.py. for help run 'python3 PinBlockScan.py help'\n")

#getCorrection(ports)
#setCorrection(ports)
#getCorrection(ports)


#port = find_Arduino()
#if(len(port)==0):
#	print("No Arduino found")
#else:
#	get_Data(port,"PinBlockScan07_26.csv")
