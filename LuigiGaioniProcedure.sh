#!/bin/bash
#writen by Zachary Franklin
#Description: while in a CROC_## dir running this program will loop though the Luigi Gaioni procedure running a threshold scan for each combination of BIAS, LDAC, and TDAC. There must be already mad csv files with the desired values of TDAC (0,16,31), and there must be a "RD53B.toml" file which has "tdac = tdac.csv", a variable called "DAC_LDAC_LIN" so we can change LDAC, and each of the locations of the BIAS variable ("DAC_PREAMP_L_LIN", "DAC_PREAMP_R_LIN", "DAC_PREAMP_TL_LIN", etc.). and there also must be a RD53BTools.toml file so we can run the ThresholdScan. If you input an argument for a directory that already exists the program skips the runs which already exist
#1 optional argument for where you want the output files to be stored. If no arguments are given a default directory will be made with a time stamp.
LDAC_vals=(130 150 170 190) #LDAC values to loop through
TDAC_vals=(0 16 31) #TDAC values to loop through
BIAS_vals=(300 250 200) #BIAS valeus to loop through
BIAS_names=("DAC_PREAMP_L_LIN" "DAC_PREAMP_R_LIN" "DAC_PREAMP_TL_LIN" "DAC_PREAMP_TR_LIN" "DAC_PREAMP_T_LIN" "DAC_PREAMP_M_LIN") #the names of the values to change to change PA_IN_BIAS_LIN
###CATCH ERRORS###
if (($# > 1)) #check if too many arguments ere passed
then
	echo "Error too many arguments given. 1 optional argument expected $# were given"
	exit
fi
if [ -f "tdac.csv" ] #check if a tdac.csv file exists to coppy the format of
then
	echo "Sample tdac file found"
else
	echo "Error no sample tdac file found expected file named: tdac.csv"
	exit
fi
for TDAC in ${TDAC_vals[@]} #check if tdac#.csv files already exist for each tdac value we will try
do
	if [ -f tdac${TDAC}.csv ] #check current and previous dir for the tdac files
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
for BIAS_loc in ${BIAS_names[@]} #loop through all bias values in toml file to make sure they exist to be replaced
do
	if [ ! -z "$(grep "$BIAS_loc" "RD53B.toml")" ] 
	then 
		echo "Found in RD53B.toml file BIAS location: $BIAS_loc"
	else
		echo "Error did not find, in RD53B.toml file, BIAS location: $BIAS_loc"
		echo "Make sure $BIAS_loc exists in RD53B.toml"
		exit
       	fi
done
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

#Create a unique name to store macro for saving plots from root
out_dest_number=0
unique_not_found=true
while $unique_not_found
do
        if [ -f "macro${out_dest_number}.C" ]; then
                let out_dest_number++
        else
                unique_not_found=false
        fi
done
macro_name="macro${out_dest_number}.C" #unique file name
touch $macro_name #create a macro for pulling pdfs out of the results root files 
trap 'rm $macro_name; echo SIGINT signal found; exit' SIGINT #cleans up in the event of a ctrl c call
echo "{" >> $macro_name
echo "        TFile *f = new TFile(\"$DIR/BIAS300_TDAC0_LDAC150/ThresholdScan/results.root\");" >> $macro_name
echo "        TCanvas *c1; gDirectory->GetObject(\"Chip board_0_hybrid_0_chip_0/S-Curves;1\",c1);" >> $macro_name
echo "        c1->Draw();" >> $macro_name
echo "        gPad->SetLogz(1);" >> $macro_name
echo "	      c1->SetWindowSize(1400,800);" >> $macro_name
echo "        c1->Print(\"$DIR/BIAS300_TDAC0_LDAC150/S_Curve_BIAS300_TDAC0_LDAC150.pdf\");" >> $macro_name
echo "        TCanvas *c2; gDirectory->GetObject(\"Chip board_0_hybrid_0_chip_0/Threshold Distribution (fitting);1\",c2);" >> $macro_name
echo "        c2->Draw();" >> $macro_name
echo "        c2->SetWindowSize(1400,800);" >> $macro_name
echo "        c2->Print(\"$DIR/BIAS300_TDAC0_LDAC150/Threshold_Dist_BIAS300_TDAC0_LDAC150.pdf\");" >> $macro_name
echo "        TCanvas *c3; gDirectory->GetObject(\"Chip board_0_hybrid_0_chip_0/Noise Distribution (probit);1\",c3);" >> $macro_name
echo "        c3->Draw();" >> $macro_name
echo "        c3->SetWindowSize(1400,800);" >> $macro_name
echo "        c3->Print(\"$DIR/BIAS300_TDAC0_LDAC150/Noise_Dist_BIAS300_TDAC0_LDAC150.pdf\");" >> $macro_name
echo "}" >> $macro_name
#cat $macro_name #use this line to check macro file is made correctly
#Create a unique name to store previous tdac values
out_dest_number=0 #number to change to find unique file name for previous tdac file
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
trap 'rm $macro_name; mv $temp_tdac_name tdac.csv; echo SIGINT signal found; exit' SIGINT #cleans up in the event of CTRL c call
#Create a unique name to store previous RD53B.toml file temporarily
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
trap 'rm $macro_name; mv $temp_tdac_name tdac.csv; mv $temp_RD53B_name RD53B.toml; echo SIGINT signal found; exit' SIGINT
input=tdac.csv #location which the RD53B.toml file points to
len_LDAC=${#LDAC_vals[@]}
len_TDAC=${#TDAC_vals[@]}
len_BIAS=${#BIAS_vals[@]}
num_comb=$(($len_LDAC * $len_TDAC * $len_BIAS))
step_num=0
num_tries=5 #number of errors allowed in a row which performing ThresholdScan
for TDAC in ${TDAC_vals[@]}
do
	if [ -f tdac${TDAC}.csv ] # setting tdac to new value
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
		rm $macro_name
		mv $temp_RD53B_name RD53B.toml
		mv $temp_tdac_name tdac.csv
		exit 
	fi
	for BIAS in ${BIAS_vals[@]}
	do
		for BIAS_loc in ${BIAS_names[@]} #loop through all bias values in toml file
		do
			sed "s/$BIAS_loc.*/$BIAS_loc = ${BIAS}/" RD53B.toml -i #change BIAS
		done
		for LDAC in ${LDAC_vals[@]}
		do
			echo "Procedure Completion Percentage:  %$((${step_num} / ${num_comb}))"
			echo "Currently running tdac = $TDAC, bias = $BIAS and ldac = $LDAC"
			dest_path="${DIR}/BIAS${BIAS}_TDAC${TDAC}_LDAC${LDAC}" #Where results will be found for this combination of LDAC and TDAC
			if [ -f "$dest_path/ThresholdScan/results.root" ] #if you are continuing a run you can skip some Threshold scans if there is no results.root file
			then
				if ([ ! -f "$dest_path/Noise_Dist_BIAS${BIAS}_TDAC${TDAC}_LDAC${LDAC}.pdf" ] || [ ! -f "$dest_path/Threshold_Dist_BIAS${BIAS}_TDAC${TDAC}_LDAC${LDAC}.pdf" ] || [ ! -f "$dest_path/S_Curve_BIAS${BIAS}_TDAC${TDAC}_LDAC${LDAC}.pdf" ])
				then
					echo "Did not find results pdfs. Trying to locate inside results.root file"
					sed "s/BIAS[0-9]*_TDAC[0-9]*_LDAC[0-9]*/BIAS${BIAS}_TDAC${TDAC}_LDAC${LDAC}/g" $macro_name -i
                                	root -b -q -l $macro_name #used to run the modified macro to pull out pdfs from root file
				fi
				echo preexisting direcotry $dest_path found skipping this combination 
			else #Run threshold scan
				mkdir "$dest_path" #create results folder
				trap 'rm $macro_name; mv $temp_tdac_name tdac.csv; mv $temp_RD53B_name RD53B.toml; rm -r $dest_path ; echo SIGINT signal found; exit' SIGINT
				sed "s/DAC_LDAC_LIN.*/DAC_LDAC_LIN = ${LDAC}/" RD53B.toml -i #change value of LDAC in RD53B.toml
				#cat tdac.csv #can use this to check if tdac.csv has been updated
				#cat RD53B.toml #can use this to check if RD53B.toml has been updated
				#run the threshold scan for this combination of LDAC and TDAC
				scan_successful=false
				cur_num_tries=0
				while [ $scan_successful == false ] && [ $cur_num_tries -lt $num_tries ] #if we run into an error
				do
					#RD53BminiDAQ -f CROC.xml -t RD53BTools.toml RegReader' #used to check if BIAS and LDAC registers changed
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
					rm $macro_name
					mv $temp_RD53B_name RD53B.toml #restore previous values in RD53B.toml
					mv $temp_tdac_name tdac.csv #restore previous values in tdac.csv
					exit
				fi
				trap 'rm $macro_name; mv $temp_tdac_name tdac.csv; mv $temp_RD53B_name RD53B.toml; echo SIGINT signal found; exit' SIGINT
				sed "s/BIAS[0-9]*_TDAC[0-9]*_LDAC[0-9]*/BIAS${BIAS}_TDAC${TDAC}_LDAC${LDAC}/g" $macro_name -i #modify macro file to access the correct files
				root -b -q -l $macro_name #used to run the modified macro to pull out pdfs from root file
				cat $macro_name
			fi
			step_num=$((step_num + 100)) #increment to keep track of percent completion
		done
	done
done
rm $macro_name #delete the temporary macro file
mv $temp_RD53B_name RD53B.toml #restore previous values in RD53B.toml
mv $temp_tdac_name tdac.csv #restore previous values in tdac.csv
