#!/bin/bash

for dir in ./*; do if [ -d $dir ]; then cd ${dir}; mkdir tmp; for file in bestIndividual*.log; do cat $file | grep -v \# | cut -d ' ' -f2 > tmp/$file; done; paste -d ' ' tmp/* > ../${dir}.fitness; rm -r tmp; cd ..; fi; done

for dir in ./*; do if [ -d $dir ]; then cd ${dir}; paste -d ' ' bestIndividual*.log.q > ../${dir}.qvalue; cd ..; fi; done

for dir in ./*; do if [ -d $dir ]; then cd ${dir}; mkdir tmp; for file in bestIndividual*.log; do cat $file | grep -v \# | cut -d ' ' -f4- | awk -F' ' 'BEGIN{}{print gsub(/1/,"")}' > tmp/$file; done; paste -d ' ' tmp/* > ../${dir}.density; rm -r tmp; cd ..; fi; done
