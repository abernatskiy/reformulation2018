#!/bin/bash

# Usage: ./movie.sh <forceGain> <sensorGain> <network>

# On most monitors, you will need to modity Bullet's
# source code to get this running. Change line 81 of
# Demos/OpenGL/GlutStuff.cpp to take 0s instead of
# width/2, height/2, then cd to build3/gmake
# (assuming you use bullet3) and rebuild the library

if [ $# -lt 7 ]; then
	echo Not enough arguments
	exit 1
elif [ $# -gt 7 ]; then
	echo Too many arguments
	exit 1
fi

source vars

CLIENT_MAIN=$CLIENT_DIR/tadrosim-graphics

CURDIR="`pwd`"
CLIENT_MAKE_LOG=$CURDIR/client_make.log
CLIENT_LOG=$CURDIR/client.log

function spawnGraphicalClientWScreenshots(){
	# Spawns a client process. Arguments:
  # $1    compilation options
	# $2    remake/noremake
  cd "$CLIENT_DIR"
	if [ ! -d screenshots ]; then
		echo Create a directory for the screenshots, and mount a 5G of tmpfs there
		exit 1
	elif [ "`mount | grep screenshots`" = "" ]; then
		echo Mount the damn ramfs\! 5G are required
		echo The command is
		echo mount -t tmpfs -o size=5G none $CLIENT_DIR/screenshots
		exit 1
	fi
  make clean > "$CLIENT_MAKE_LOG" 2>&1
  make tadrosim-graphics-screenshots MORECFLAGS="$1" >> "$CLIENT_MAKE_LOG" 2>&1
	./tadrosim-graphics-screenshots in out > "$CLIENT_LOG" &
	CLIENT_PID=$!
	cd "$CURDIR"
#	echo Spawned a client process, PID $CLIENT_PID
}

function checkPIDExistence(){
	kill -0 $1 > /dev/null 2>&1
}

function waitForPID(){
	while (checkPIDExistence $1); do
		sleep 0.1
	done
}

function grabMovie(){
	cd "$CLIENT_DIR/screenshots"
	mencoder mf://*.tga -mf w=1280:h=720:fps=30:type=tga -ofps 30 -ovc x264 -x264encopts subq=1:frameref=1:pass=1:threads=2 -nosound -of lavf -o output.mkv
	mencoder mf://*.tga -mf w=1280:h=720:fps=30:type=tga -ofps 30 -ovc x264 -x264encopts subq=6:partitions=all:8x8dct:me=umh:frameref=5:bframes=3:weight_b:bitrate=3500:pass=2:threads=2 -nosound -of lavf -o output.mkv
	rm *.tga
	mv output.mkv "$CURDIR/$1"
	cd "$CURDIR"
}

spawnGraphicalClientWScreenshots "-DFORCE_GAIN=${1}f -DSENSOR_GAIN=${2}f"
echo $@ | cut -d' ' -f3- > $CLIENT_DIR/in

cat $CLIENT_DIR/out &
echo CRASHLANDING > $CLIENT_DIR/in &

waitForPID $CLIENT_PID

sync

grabMovie "fg${1}sg${2}nw`echo $@ | cut -d' ' -f4- | sed -e 's/ //g'`.mkv"

# fallback
# recordmydesktop --fps 25 --windowid $CLIENT_WINDOWID --no-sound --overwrite -o fg${1}sg${2}nw`echo $@ | cut -d' ' -f4- | sed -e 's/ //g'`.ogv &
# RMD_PID=$!
# CLIENT_WINDOWID=`wmctrl -l | grep "Bullet Physics Demo. http:\/\/bulletphysics.com" | cut -d' ' -f1`
