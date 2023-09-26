#!/bin/bash
#writen by Zachary Franklin
#1 optional argument for where you want the output files to be stored. If no arguments are given a default directory will be made with a time stamp.	
#for info on this program read the READ_ME.txt in the tuningHelpers directory
helpers_name="tuningHelpers"
LDAC_vals=(130 150 170 190) #LDAC values to loop through
TDAC_vals=(0 16 31) #TDAC values to loop through
BIAS_vals=(300 250 200) #BIAS valeus to loop through
BIAS_names=("DAC_PREAMP_L_LIN" "DAC_PREAMP_R_LIN" "DAC_PREAMP_TL_LIN" "DAC_PREAMP_TR_LIN" "DAC_PREAMP_T_LIN" "DAC_PREAMP_M_LIN") #the names of the values to change to change PA_IN_BIAS_LIN

###CATCH ERRORS###
if (($# > 1)) #check if too many arguments are passed
then
	echo "Error too many arguments given. 1 optional argument expected $# were given"
	exit
fi
if [ -d $helpers_name ] #Check that the directory exists with all the files we will need
then
	echo "Helper directory found"
else
	echo "Error no $helpers_name directory found make sure you are calling this script from the CROC directory"
	exit
fi
if [ -f "CROC.xml" ]
then
	echo "CROC.xml file found"
else
	echo "Error CROC.xml file not found. Make sure this file exists so we can run RD53BminiDAQ"
	exit
fi
if [ -f "tdac.csv" ] #check if a tdac.csv file exists to copy the format of
then
	echo "Sample tdac file found"
else
	echo "Error no sample tdac file found expected file named: tdac.csv"
	exit
fi
for TDAC in ${TDAC_vals[@]} #check if tdac#.csv files already exist for each tdac value we will try
do
	if [ -f $helpers_name/tdac${TDAC}.csv ]
	then
		echo "$helpers_name/tdac${TDAC}.csv file found"
	elif [ -f tdac${TDAC}.csv ] #check current and previous dir for the tdac files
        then
                echo "tdac${TDAC}.csv file found"
        elif [ -f ../tdac${TDAC}.csv ]
        then
		echo "../tdac${TDAC}.csv file found"
        elif [ -f ../../tdac${TDAC}.csv ]
        then
                echo "../../tdac${TDAC}.csv file found"
        else
                echo "couldnt find a tdac${TDAC}.csv file"
		exit
        fi
done
if [ -f "RD53B.toml" ] #check if the RD53B.toml file exists to modify the LDAC value
then
	echo "RD53B.toml file found"
else
	echo "Error TD53B.toml file not found"
	exit
fi
if [ -f "RD53BTools.toml" ] #check that the TD53BTools.toml file exists so we can run RD53BminiDAQ
then
	echo "RD53BTools.toml file found"
else
	echo "Error RD53BTools.toml file not found"
        exit
fi
###END CATCH ERRORS###

if [ $# == 1 ] #check if we have an argument for a custom results dir
then
	DIR=$1
        echo "Using custom directory name: $DIR"
else #else we will make a default dir
	DIR=Luigi_Gaioni_Procedure_Results_"$(date +"%m_%d_%y_%T")"
        echo "Using default directory name: $DIR"
fi
if [ -d $DIR ] #check if the directory already exists
then
	echo "Using preexisting directory :$DIR"
else
	echo "Making results directory :$DIR"
	mkdir $DIR #create results dir
fi
macro_name="$helpers_name/macro.C" #premade macro for pulling out pdfs in tuningHelpers directory
if [ -f $macro_name ]
then
	sed "s/([^\/]*\//(\"$DIR\//g" $macro_name -i
else
	echo "Could not find $helpers_name/macro.C. Make sure you are calling this script from outside $helpers_name directory inside the CROC directory"
fi
###Create duplicates of the tdac.csv, CROC.xml, and RD53B.toml files to ensure no altered/lost data ###

##tdac.csv##
out_dest_number=0
unique_not_found=true
while $unique_not_found
do
	if [ -f "temp${out_dest_number}.csv" ]; then
		let out_dest_number++
	else
		unique_not_found=false
	fi
done
temp_tdac_name="temp${out_dest_number}.csv" #unique file name
cp tdac.csv $temp_tdac_name #copy previous tdac values to a temporary file
trap 'mv $temp_tdac_name tdac.csv; echo SIGINT signal found; trap - INT; exit' SIGINT #cleans up in the event of CTRL c call
##END tdac.csv##

##CROC.xml##
out_dest_number=0 #number to change to find unique file name for previous CROC.xml file
unique_not_found=true
while $unique_not_found
do
        if [ -f "temp${out_dest_number}.xml" ]; then
                let out_dest_number++
        else
                unique_not_found=false
        fi
done
temp_CROC_name="temp${out_dest_number}.xml" #unique file name
cp CROC.xml $temp_CROC_name #copy previous tdac values to a temporary file
trap 'mv $temp_CROC_name CROC.xml; mv $temp_tdac_name tdac.csv; echo SIGINT signal found; trap - INT; exit' SIGINT #cleans up in the event of CTRL c call
##END CROC.xml##

##RD53B.toml##
out_dest_number=0
unique_not_found=true
while $unique_not_found
do
        if [ -f "temp${out_dest_number}.toml" ]; then
                let out_dest_number++
        else
                unique_not_found=false
        fi
done
temp_RD53B_name="temp${out_dest_number}.toml" #new temporary RD53B.toml loaction
cp RD53B.toml $temp_RD53B_name #copy previous RD53B.toml to tempoorary location
trap 'mv $temp_CROC_name CROC.xml; mv $temp_tdac_name tdac.csv; mv $temp_RD53B_name RD53B.toml; echo SIGINT signal found; trap - INT; exit' SIGINT
##END RD53B.toml##
###END creating Duplicate Files###
if [ ! -z "$(grep "\[Registers\]" "RD53B.toml")" ]
then
	echo "Found [Registers] tag in RD53B.toml file"
else
	echo "Did not find [Registers] tag adding tag to RD53B.toml file"
	echo "[Registers]" >> RD53B.toml
fi
for BIAS_loc in ${BIAS_names[@]} #loop through all bias values in toml file to make sure they exist to be replaced
do
        if [ ! -z "$(grep "$BIAS_loc" "RD53B.toml")" ]
        then
                echo "Found BIAS variable ($BIAS_loc) in RD53B.toml file"
        else
		echo "Did not find $BIAS_loc adding $BIAS_loc to RD53B.toml file"
		sed "/\[Registers\]/a $BIAS_loc = 300" RD53B.toml -i
        fi
cat RD53B.toml
done
if [ ! -z "$(grep "DAC_LDAC_LIN" "RD53B.toml")" ]
then
	echo "Found LDAC variable in RD53B.toml file"
else
	echo "Did not find LDAC variable. Adding DAC_LDAC_LIN to RD53B.toml file"
	sed "/\[Registers\]/a DAC_LDAC_LIN = 130" RD53B.toml -i
fi

cat RD53B.toml
len_LDAC=${#LDAC_vals[@]}
len_TDAC=${#TDAC_vals[@]}
len_BIAS=${#BIAS_vals[@]}
num_comb=$(($len_LDAC * $len_TDAC * $len_BIAS))
step_num=0
num_tries=5 #number of errors allowed in a row which performing ThresholdScan
for TDAC in ${TDAC_vals[@]}
do
	if [ -f $helpers_name/tdac${TDAC}.csv ]
	then
		cp $helpers_name/tdac${TDAC}.csv tdac.csv
	elif [ -f tdac${TDAC}.csv ] # setting tdac to new value
	then
		cp tdac${TDAC}.csv tdac.csv
	elif [ -f ../tdac${TDAC}.csv ]
	then
		cp ../tdac${TDAC}.csv tdac.csv
	elif [ -f ../../tdac${TDAC}.csv ]
	then
		cp ../../tdac${TDAC}.csv tdac.csv
	else
		echo "couldnt find a tdac${TDAC}.csv file"
		mv $temp_RD53B_name RD53B.toml
		mv $temp_tdac_name tdac.csv
		mv $temp_CROC_name CROC.xml
		trap - INT
		exit
	fi
	for BIAS in ${BIAS_vals[@]}
	do
		for BIAS_loc in ${BIAS_names[@]} #loop through all bias values in toml file
		do
			sed "s/$BIAS_loc.*/$BIAS_loc = ${BIAS}/" RD53B.toml -i #change BIAS in RD53B.toml
			sed "s/$BIAS_loc.*/$BIAS_loc = \"${BIAS}\"/" CROC.xml -i #change BIAS in CROC.xml
		done
		for LDAC in ${LDAC_vals[@]}
		do
			echo "Procedure Completion Percentage:  %$((${step_num} / ${num_comb}))"
			echo "Currently running tdac = $TDAC, bias = $BIAS and ldac = $LDAC"
			dest_path="${DIR}/BIAS${BIAS}_TDAC${TDAC}_LDAC${LDAC}" #Where results will be found for this combination of LDAC and TDAC
			if [ -f "$dest_path/ThresholdScan/results.root" ] #if you are continuing a run you can skip some hreshold scans
			then
				if ([ ! -f "$dest_path/Noise_Dist_BIAS${BIAS}_TDAC${TDAC}_LDAC${LDAC}.pdf" ] || [ ! -f "$dest_path/Threshold_Dist_BIAS${BIAS}_TDAC${TDAC}_LDAC${LDAC}.pdf" ] || [ ! -f "$dest_path/S_Curve_BIAS${BIAS}_TDAC${TDAC}_LDAC${LDAC}.pdf" ])
				then
					echo "Did not find results pdfs. Trying to locate inside results.root file"
					sed "s/BIAS[0-9]*_TDAC[0-9]*_LDAC[0-9]*/BIAS${BIAS}_TDAC${TDAC}_LDAC${LDAC}/g" $macro_name -i
                                	root -b -q -l $macro_name #used to run the modified macro to pull out pdfs from root file
				fi
				echo preexisting direcotory $dest_path found skipping this combination 
			else #Run threshold scan
				if [ -d $dest_path ]
				then
					rm -r $dest_path #removes old dir if it exists
				fi
				mkdir "$dest_path" #create results folder
				trap 'mv $temp_CROC_name CROC.xml;mv $temp_tdac_name tdac.csv; mv $temp_RD53B_name RD53B.toml; rm -r $dest_path ; echo SIGINT signal found; trap - INT; exit' SIGINT
				sed "s/DAC_LDAC_LIN.*/DAC_LDAC_LIN = ${LDAC}/" RD53B.toml -i #change value of LDAC in RD53B.toml
				sed "s/DAC_LDAC_LIN.*/DAC_LDAC_LIN = \"${LDAC}\"/" CROC.xml -i #change LDAC in CROC.xml
				scan_successful=false
				cur_num_tries=0
				while [ $scan_successful == false ] && [ $cur_num_tries -lt $num_tries ] #if we run into an error
				do
					#used to confirm BIAS and LDAC registers changed
					RD53BminiDAQ -f CROC.xml -t RD53BTools.toml RegReader | tee ${dest_path}/Current_Registers_BIAS${BIAS}_TDAC${TDAC}_LDAC${LDAC}.txt
					#used to run the threshold scan
					RD53BminiDAQ -f CROC.xml -t RD53BTools.toml -o $dest_path -h ThresholdScan | tee ${dest_path}/Console_Log_BIAS${BIAS}_TDAC${TDAC}_LDAC${LDAC}.txt
					if [ -d "$dest_path/ThresholdScan" ]
					then
						scan_successful=true
					fi
					let cur_num_tries++
				done
				if [ $scan_successful == false ]
				then
					echo "Error: ran into $num_tries errors in a row while running ThresholdScan"
					rm -r $dest_path
					mv $temp_RD53B_name RD53B.toml #restore previous values in RD53B.toml
					mv $temp_tdac_name tdac.csv #restore previous values in tdac.csv
					mv $temp_CROC_name CROC.xml
					trap - INT
					exit
				fi
				trap 'mv $temp_CROC_name CROC.xml; mv $temp_tdac_name tdac.csv; mv $temp_RD53B_name RD53B.toml; echo SIGINT signal found; trap - INT; exit' SIGINT
				sed "s/BIAS[0-9]*_TDAC[0-9]*_LDAC[0-9]*/BIAS${BIAS}_TDAC${TDAC}_LDAC${LDAC}/g" $macro_name -i #modify macro file to access the correct files
				root -b -q -l $macro_name #used to run the modified macro to pull out pdfs from root file
			fi
			step_num=$((step_num + 100)) #increment to keep track of percent completion
		done
	done
done
mv $temp_CROC_name CROC.xml
mv $temp_RD53B_name RD53B.toml #restore previous values in RD53B.toml
mv $temp_tdac_name tdac.csv #restore previous values in tdac.csv

