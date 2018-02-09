#!/bin/bash

# Takes a single argument - the name of the file to process

CURDIR=`pwd`

WORKDIR="${HOME}/findcommunities/"
QCOMPUTER="${WORKDIR}massQ.sh"

TXTPIPE="/tmp/txt_${1}"
BINPIPE="/tmp/bin_${1}"

mkfifo "$TXTPIPE"
mkfifo "$BINPIPE"

cd $WORKDIR

for file in ${CURDIR}/${1}*.log; do
	echo $file
	cat "${file}" | tail -n +2 | cut -d ' ' -f2- | $QCOMPUTER $TXTPIPE $BINPIPE | cut -d ' ' -f2 > ${file}.q
done

cd $CURDIR

rm "$TXTPIPE"
rm "$BINPIPE"
