#!/bin/bash

# Usage: getFitnessTimeSeriesForParams.sh forceGain sensorGain connectionCost randomSeedsFileName

source evscripts-funcs

CURFILENAME="./fg${1}sg${2}cc${3}_fitnessTimeSeries.dat"
CHAMPFILENAME="./fg${1}sg${2}cc${3}_champs.dat"
echo "# FG ${1} SG ${2} CC ${3}. Fitness time series are based on random seeds from ${4}." > $CURFILENAME
echo "# FG ${1} SG ${2} CC ${3}. Champions are based on random seeds from ${4}." > $CHAMPFILENAME

spawnClient "-DFORCE_GAIN=${1}f -DSENSOR_GAIN=${2}f -DCONNECTION_COST=0.f"

IFS=$'\n'
for rseed in `cat ${4}`; do
	spawnEVS $rseed ${3}
	waitForPID $EVS_PID
	cat "$EVS_RESULTS" | awk '{print $2}' | tail -n +2 | tr '\n' ' ' >> $CURFILENAME
	cat "$EVS_RESULTS" | tail -1 | cut -d ' ' -f4- >> $CHAMPFILENAME
	echo >> $CURFILENAME
done

kill $CLIENT_PID
