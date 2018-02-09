#!/bin/bash

ps aux | grep main.py | grep -v grep | grep -v nano
ps aux | grep tadrosim | grep -v grep | grep -v nano
