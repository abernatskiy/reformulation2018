#!/bin/bash

makeParetoHistogram() {
	dir="$1"
	method="$2"
	for file in ./${dir}/initialPopulationType:${method}*/paretoFront_gen*.log ; do
		wc -l $file
	done | cut -d ' ' -f1 | sort -n | uniq -c > ${dir}/paretoHistogram${method}
}

for dir in */; do
	for method in random sparse; do
		echo $dir $method
		makeParetoHistogram "$dir" "$method"
	done
done
