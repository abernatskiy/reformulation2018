#!/bin/bash

CURDIR=`pwd`

WORKDIR="/home/iriomotejin/findcommunities/"
QCOMPUTER="${WORKDIR}massQ.sh"

cd $WORKDIR

for file in ${CURDIR}/bestIndividual*.log; do
	cat $file | tail -n +2 | cut -d ' ' -f3- | $QCOMPUTER | cut -d ' ' -f2 > ${file}.q
done

paste -d ' ' *.log.q > qvalues

cd $CURDIR
