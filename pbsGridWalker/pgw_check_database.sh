#!/bin/bash

if [[ -z `sqlite3 "$1" '.dump GridQueue' | grep INSERT | grep -v ',1,1,0,0);'` ]]; then
	echo Database is clear;
else
	echo Database has unfinished or failed jobs;
fi
