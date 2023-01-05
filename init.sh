#!/bin/bash

for var in "$@"
do
	mkdir "$var"
	mkdir "$var"/Results
	mkdir "$var"/tmp
	mkdir "$var"/Results/GlobalThresholdTuning
	mkdir "$var"/Results/ThresholdEqualization
	mkdir "$var"/Results/MuxScan
	mkdir "$var"/Results/ShortRingOsc
	mkdir "$var"/Results/ThresholdScan
	mkdir "$var"/Results/TempSensor
done
