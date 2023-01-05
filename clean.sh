#!/bin/bash

for croc in $(ls -d CROC*/)
do
	for dir in $(ls $croc/Results/)
	do
		rm -rf $croc/Results/"$dir"/*
		echo "Deleting $dir from $croc Results"
	done
done
