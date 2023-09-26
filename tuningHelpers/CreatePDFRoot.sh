#!/bin/bash
LDAC_vals=(130 150 170 190) #LDAC values to loop through
TDAC_vals=(0 16 31) #TDAC values to loop through
BIAS_vals=(300 250 200) #BIAS valeus to loop throughiut_dest_number=0
if [ $# == 1 ] #check if we have an argument for a custom results dir
then
        DIR=$1
else #else we will make a default dir
        echo "Required argument Not given. Must have the directory which was used for the tuning given as an argument"
return
fi
if [ -d $DIR ] #check if the directory already exists
then
        echo "Using the preexisting directory :$DIR"
else
        echo "The supplied argument must be a path to a preexisting directory with the tuning results"
fi
macro_name = "macro.C"
if [ -f $macro_name ]
then
	echo "Root macro found" 
	sed "s/([^\/]*\//(\"$DIR\//g" $macro_name -i
else
	echo "No root macro found"
	exit
fi
step_num=0
for TDAC in ${TDAC_vals[@]}
do
        for BIAS in ${BIAS_vals[@]}
        do
                for LDAC in ${LDAC_vals[@]}
                do
                        echo "Procedure Completion Percentage:  %$((${step_num} / ${num_comb}))"
                        echo "Currently creating PDF for: tdac = $TDAC, bias = $BIAS and ldac = $LDAC"
                        dest_path="${DIR}/BIAS${BIAS}_TDAC${TDAC}_LDAC${LDAC}" #Where results will be found for this combination of LDAC and TDAC
                        if [ -f "$dest_path/ThresholdScan/results.root" ] #if you are continuing a run you can skip some hreshold scans
                        then
                                if ([ ! -f "$dest_path/Noise_Dist_BIAS${BIAS}_TDAC${TDAC}_LDAC${LDAC}.pdf" ] || [ ! -f "$dest_path/Threshold_Dist_BIAS${BIAS}_TDAC${TDAC}_LDAC${LDAC}.pdf" ] || [ ! -f "$dest_path/S_Curve_BIAS${BIAS}_TDAC${TDAC}_LDAC${LDAC}.pdf" ])
                                then
                                        echo "Did not find results pdfs. Trying to locate inside results.root file"
                                        sed "s/BIAS[0-9]*_TDAC[0-9]*_LDAC[0-9]*/BIAS${BIAS}_TDAC${TDAC}_LDAC${LDAC}/g" $macro_name -i
					root -b -q -l $macro_name #used to run the modified macro to pull out pdfs from root file
                                fi
                                echo preexisting directory $dest_path found skipping this combination 
                        else #Run threshold scan
                              	echo "No results.root found for this combination. Skipping to the next one"
			fi 
                        step_num=$((step_num + 100)) #increment to keep track of percent completion 
                done 
	done 
done
