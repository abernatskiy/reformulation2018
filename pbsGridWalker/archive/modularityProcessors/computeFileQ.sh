#!/bin/bash

# Takes a single argument - the name of the file to process

CURDIR=`pwd`

WORKDIR="${HOME}/findcommunities/"
QCOMPUTER="${WORKDIR}massQ.sh"

TXTPIPE="/tmp/txt_${1}_${BASHPID}"
BINPIPE="/tmp/bin_${1}_${BASHPID}"

mkfifo "$TXTPIPE"
mkfifo "$BINPIPE"

cd $WORKDIR

cat ${CURDIR}/$1 | tail -n +2 | cut -d ' ' -f3- | $QCOMPUTER $TXTPIPE $BINPIPE | cut -d ' ' -f2 > ${CURDIR}/${1}.q

cd $CURDIR

rm "$TXTPIPE"
rm "$BINPIPE"
