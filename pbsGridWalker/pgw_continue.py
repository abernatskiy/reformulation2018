#!/usr/bin/env python2

import argparse
cliParser = argparse.ArgumentParser(description='Continues a stalled experiment')
cliParser.add_argument('scriptPath', metavar='path_to_script', type=str, help='path to the description script')
cliArgs = cliParser.parse_args()

from pgw_experiment import Experiment
import gridSql
e = Experiment(cliArgs.scriptPath)
e.enterWorkDir()
gridSql.resetInProgressPoints(e.dbname)
e.exitWorkDir()
e.run()
e.processResults()
