#!/bin/bash

# A scripts to generate the final scripts for the gigantic convergence experiment

generateOneScript() {
	local base_script="${1}"
	local num_segments="${2}"
	local population_size="${3}"
	local stop_after_generations="${4}"
	local pareto_logging_period="${5}"
	local queue="${6}"
	local requested_time="${7}"
	local max_jobs="${8}"
	local points_per_job="${9}"
	local simulation_time="${10}"
	local simulation_time_step="${11}"
	local stages="${12}"
	local indiv_classes="${13}"
	cat "${base_script}.py" | sed \
		-e "s/segments = [0-9]*/segments = ${num_segments}/" \
		-e "s/'genStopAfter': [0-9]*/'genStopAfter': ${stop_after_generations}/" \
		-e "s/'populationSize': [0-9]*/'populationSize': ${population_size}/" \
		-e "s/'logParetoFrontPeriod': [0-9]*/'logParetoFrontPeriod': ${pareto_logging_period}/" \
		-e "s/queue = '[a-z]*'/queue = '${queue}'/" \
		-e "s/maxJobs = [0-9]*/maxJobs = ${max_jobs}/" \
		-e "s/pointsPerJob = [0-9]*/pointsPerJob = ${points_per_job}/" \
		-e "s/expectedWallClockTime = '.*'/expectedWallClockTime = '${requested_time}'/" \
		-e "s/'simulationTime': [\.0-9]*/'simulationTime': ${simulation_time}/" \
		-e "s/'timeStep': [\.0-9]*/'timeStep': ${simulation_time_step}/" \
		-e "s/stagesToConsider = [0-9]*/stagesToConsider = ${stages}/" \
		-e "s/'compositeClass0', \[.*\]/'compositeClass0', \[${indiv_classes}\]/" > "autoscripts/${base_script}_N${num_segments}.py"
}

generateFromOneBase() {
	local base_script="${1}"
	# Regarding convergence times: about 100 gens for 3 segments at probability of morphological mutation of 0.2, 400 for 5, 10 gets stuck indefinitely.
	# The times are doubled where known and for 10 segments a placeholder 2000 is used for now
	generateOneScript "${base_script}" 3 50 600 50 'shortq' '03:00:00' 50 90 '10.0' '0.1' 5 "'integerVectorSymmetricRangeMutations', 'integerVectorRandomJumps'"
	generateOneScript "${base_script}" 5 100 1600 100 'workq' '30:00:00' 200 45 '10.0' '0.1' 5 "'integerVectorSymmetricRangeMutations', 'integerVectorRandomJumps'"
	generateOneScript "${base_script}" 10 200 4000 100 'workq' '30:00:00' 400 1 '10.0' '0.1' 5 "'integerVectorSymmetricRangeMutations', 'integerVectorRandomJumps'"
}

generateFromOneBase rateSwipe
generateFromOneBase rateSizeSwipe
generateFromOneBase ccSwipe
