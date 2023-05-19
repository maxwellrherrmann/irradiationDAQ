import os
import subprocess
import csv
import sys
import numpy as np

# This script is for parsing the irradiation data into nicer csv files for mux scan data, ring oscillator data, and temperature data into 3 separate csv files

# there are basically 4 data sets: data collected over the weekend for CROC_54 with data stored in the CROC_54/Results/*Weekend*, data collected for CROC_57 until around 6:45 a.m. on Jan 10,
# (this is in CROC_57/Results) and data collected on CROC_57 with (unfortunately) the configuration of CROC_54 from around 10:45 a.m. Jan 10 through the 12th at some point,
# which is stored in CROC_54/Results (sorry for the confusion) then the data collected by steve on the 13th (stored here in steve_data with the file containing timestamps)

# For convenience I copied the CROC_54 and CROC_57 folders out of irradiationDAQ where they normally live (and remain in duplicate)


#for parsing irradiationDAQ data uncomment the """ lines below and comment out the steve data lines
#time_line refers to which line in the terminal_dump.txt file to scrape for a timestamp, varies from CROC_54 to CROC_57 for some reason

daq_path = '.'
# croc = 'CROC_57'
croc = 'CROC_5D'
result_dir = '57_config'
out_dir = 'CROC_5D_out'
#result_dir = 'Weekend_1_6-1_9_Results'
time_line = 42
# time_line = 45

#for parsing steve data
# daq_path = 'steve_data'
# result_dir = 'Results'

#croc, result_dir, log_file = sys.argv[1], sys.argv[2], sys.argv[3]

#to be used for sorting and others, grabs index from end of file name
def get_index(scan):
    return int(scan[scan.index('_')+1:])

#this reads a single muxScan.csv file and returns a parsed row of data
def parse_mux_file(file):
    fields = {'TIME':0}

    with open(file, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        lines = [line for line in reader]
        for line in lines[1:]:
            fields[line[1][1:]]=float(line[2])

    with open(file[:-11]+'terminal_dump.txt', 'r') as f:
        lines = f.readlines()
        fields['TIME'] = lines[time_line][:16]

    return fields

#same as the parse_mux_file() function but for ring oscillator data
def parse_osc_file(file):
    fields = {'TIME':0}
    l=[]

    with open(file, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for line in reader:
            l.append(line)

    with open(file[:-19]+'terminal_dump.txt', 'r') as f:
        lines = f.readlines() 
        fields['TIME'] = lines[time_line][:16]

    # Fixes problem with weird duplicate names in the csv file. The length of the headers is +2 of
    names = l[0]+l[1][1:]
    names = [name.strip().replace(' ', '_') for name in names]
    names = list(dict.fromkeys(names))
    vals = l[2]

    for i,name in enumerate(names):
        fields[name]=float(vals[i]) 

    return fields

#same idea as the other two, but works differently - needs the terminal_dump.txt style file
def parse_temp_file(file):
    x = []
    t = ''
    d = {'TIME':0, 'TEMPERATURE':0}

    with open(file, 'r') as f:
        lines = f.readlines()

        for line in lines:
            if 'TEMPERATURE' in line:
                x.append(float(line[71:81].strip()))

        t = lines[time_line][:16]
    d['TIME']=t
    d['NTC_Temp'] = np.mean(x)

    return d

#this runs all three on all the files in either CROC_54 or CROC_57
def parse_files(scan_name):
    #format: name of destination file, name of single input file, base folder name, parse function, probably a headers list
    scan_dict = {'mux':['muxScans', 'muxScan.csv', 'MuxScan', parse_mux_file, []], 
                 'osc':['shortOscillators', 'shortOscillator.csv', 'ShortRingOsc', parse_osc_file, []], 
                 'temp':['tempScans', 'terminal_dump.txt', 'TempSensor', parse_temp_file, ['INDEX', 'TIME', 'NTC_Temp']]
                 }

    path = f'{daq_path}/{croc}/{result_dir}/{scan_dict[scan_name][2]}/'
    scans = os.listdir(path)
    scans.sort(key=get_index)

    with open(f'{out_dir}/{scan_dict[scan_name][0]}_{croc}_{result_dir}.csv', 'w') as out:
        writer = csv.writer(out, delimiter=',')
        first_file = f'{path}{scans[0]}/{scan_dict[scan_name][1]}'
        if os.path.exists(first_file):
            first_d = scan_dict[scan_name][3](first_file)
            writer.writerow(['INDEX'] + list(first_d.keys()))
            writer.writerow([get_index(scans[0])] + list(first_d.values()))
        for scan in scans[1:]:
            file = path + scan +'/'+ scan_dict[scan_name][1]
            if os.path.exists(file):
                d = scan_dict[scan_name][3](file)
                writer.writerow([get_index(scan)]+list(d.values()))

# ========================= ========================= ========================= ========================

#needed a different function for parsing the data as steve has it
def steve_parse_osc_file(file, n):
    fields = {'TIME':0}
    l=[]

    with open(file, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for line in reader:
            l.append(line)

    with open('steve_data/files_in_Results_for_201.57_irradiation.txt') as f:
        lines = f.readlines()
        for line in lines:
            if f'ShortRingOsc_{n}' in line:
                date = line[34:42]
                date = date.strip()
                date='2023-01-'+date
                fields['TIME'] = date

    names = l[0]+l[1][1:]
    names = [name.strip().replace(' ', '_') for name in names]
    vals = l[2]

    for i,name in enumerate(names):
        fields[name]=float(vals[i]) 

    return fields

#needed a different function for parsing the data as steve has it
def steve_parse_mux_file(file, i):
    fields = {'TIME':0}

    with open(file, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        lines = [line for line in reader]
        for line in lines[1:]:
            fields[line[1][1:]]=float(line[2])

    with open('steve_data/files_in_Results_for_201.57_irradiation.txt') as f:
        for line in f.readlines():
            if f'MuxScan_{i}' in line:
                fields['TIME'] = '2023-01-'+ line[34:42].strip()

    return fields

#These do the parsing for all the "steve data" ring oscillator files
def steve_parse_osc(start, end):
    with open('fixed_parse_04_23_23/steve_osc.csv', 'a') as f:
        writer = csv.writer(f, delimiter=',')
        first = range(start,end)[0]
        first_file = f'steve_data/Results/ShortRingOsc_{first}/shortOscillator.csv' 
        if os.path.exists(first_file):
            first_d = steve_parse_osc_file(first_file, first)
            writer.writerow(['INDEX']+list(first_d.keys()))
        for i in range(start, end):
            file = f'steve_data/Results/ShortRingOsc_{i}/shortOscillator.csv'
            if os.path.exists(file):
                d= steve_parse_osc_file(file, i)
                writer.writerow([i]+list(d.values()))

#These do the parsing for all the "steve data" mux files
def steve_parse_mux(start, end):
    with open('testing_parse/steve_mux.csv', 'a') as f:
        writer = csv.writer(f, delimiter=',')
        first = range(start,end)[0]
        first_file = f'steve_data/Results/MuxScan_{first}/muxScan.csv' 
        if os.path.exists(first_file):
            first_d = steve_parse_mux_file(first_file, first)
            writer.writerow(['INDEX']+list(first_d.keys()))
        for i in range(start, end):
            file = f'steve_data/Results/MuxScan_{i}/muxScan.csv'
            if os.path.exists(file):
                d = steve_parse_mux_file(file, i)
                writer.writerow([i]+list(d.values()))

# Below the functions are actually called, sensitive to the settings at the top of the script

# I dealt with steve temperature files manually, that was just a little too annoying to bother coding up

# steve_parse_osc(296, 332)
# steve_parse_mux(424,436)

# parse_files('mux')
parse_files('osc')
# parse_files('temp')
