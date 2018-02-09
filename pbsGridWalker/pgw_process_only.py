#!/usr/bin/env python2

import argparse
cliParser = argparse.ArgumentParser(description='Run only the data processing part of any experiment description script')
cliParser.add_argument('scriptPath', metavar='path_to_script', type=str, help='path to the description script')
cliArgs = cliParser.parse_args()

from pgw_experiment import Experiment
e = Experiment(cliArgs.scriptPath)
e.processResults()
