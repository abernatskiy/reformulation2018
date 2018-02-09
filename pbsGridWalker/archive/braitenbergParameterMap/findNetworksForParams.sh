#!/bin/bash

source evscripts-funcs

echo -n "force_gain: ${1} sensor_gain: ${2}" >> $RESULTS
spawnClient "-DFORCE_GAIN=${1}f -DSENSOR_GAIN=${2}f"
for i in 7881 1543 106 4899 8591 6604 4356 4775 7870 7317; do
	spawnEVS $i
	waitForPID $EVS_PID
	echo -n " " >> $RESULTS
	echo -n seed${i}: `tail -1 "$EVS_RESULTS" | cut -d " " -f 2-` >> $RESULTS
done
kill $CLIENT_PID
echo >> $RESULTS
