#!/usr/bin/python2

# Parsing CLI

import argparse

cliParser = argparse.ArgumentParser(description='EVolutionary Server implementation based on INI config files', epilog='For config format see exampleConfig.ini')
cliParser.add_argument('evalsFileName', metavar='evalsFileName', type=str, help='file or pipe for incoming individual evaluations')
cliParser.add_argument('indivFileName', metavar='indivFileName', type=str, help='file or pipe for outgoing individual genomes')
cliParser.add_argument('randSeed', metavar='randSeed', type=int, help='integer to be used as random seed')
cliParser.add_argument('configFileName', metavar='configFileName', type=str, help='config file')

cliArgs = cliParser.parse_args()

# Parsing the config file

import ConfigParser

conf = ConfigParser.RawConfigParser()
conf.optionxform = str # required to keep the uppercase-containing fields working
conf.read(cliArgs.configFileName)

# Loading the appropriate implementation of the three main classes: Individual, Evolver and Communicator

import importlib

Individual = importlib.import_module('individuals.' + conf.get('classes', 'individual')).Individual
Evolver = importlib.import_module('evolvers.' + conf.get('classes', 'evolver')).Evolver
Communicator = importlib.import_module('communicators.' + conf.get('classes', 'communicator')).Communicator

# Loading parameters

def loadDict(conf, section):
	return { parName: parVal for parName, parVal in conf.items(section) }

indivParams = loadDict(conf, 'indivParams')
evolParams = loadDict(conf, 'evolParams')
evolParams['indivClass'] = Individual
if evolParams.has_key('randomSeed'):
	print('WARNING: CLI supplied random seed overriden by the one supplied in the config file. New value: ' + str(evolParams['randomSeed']))
else:
	evolParams['randomSeed'] = int(cliArgs.randSeed)

# Creating communicator and evolver objects
# This causes the initial population to be evaluated

comm = Communicator(cliArgs.evalsFileName, cliArgs.indivFileName)

initialPopulationFileName = None if not evolParams.has_key('initialPopulationFile') else evolParams['initialPopulationFile']
evolver = Evolver(comm, indivParams, evolParams, initialPopulationFileName=initialPopulationFileName)

# Config-dependent backup function: doesn't do anything unless evolver.params['backup'] == 'yes'
# Will make backups at every generation if evolver.params['backupPeriod'] is not set, otherwise
# will make a backup once every evolver.params['backupPeriod'] iterations
evolver.pickleSelf()
evolver.generateLogsAndStdout()

# Running the evolution
while True:
	# Advance evolution by one generation, whatever that means
	evolver.updatePopulation()

	evolver.pickleSelf()
	evolver.generateLogsAndStdout()
