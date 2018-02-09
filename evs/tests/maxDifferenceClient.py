#!/usr/bin/python2

def read(filename):
	genomes = []
	fin = open(filename, 'r')
	for line in fin:
		genomes.append(line)
	fin.close()
	return genomes

def parseGenome(genStr):
	fields = genStr.split()
	return (int(fields[0]), map(float, fields[1:]))

def evaluateGenome(parsedGenome):
	id, fields = parsedGenome
	eval = 0.0
	mult = 1.0
	for f in fields:
		eval += mult*f
		mult = -1.0 if mult==1.0 else 1.0
	eval = eval if eval>0 else -1.0*eval
	return (id, eval)

def evalToStr(eval):
	id, value = eval
	return str(id) + ' ' + str(value)

def write(filename, evalStrs):
	fout = open(filename, 'w')
	for evalStr in evalStrs:
		fout.write(evalStr + '\n')
	fout.close()

import argparse

cliParser = argparse.ArgumentParser(description='Test client which likes it when the difference between the adjacent genes is high.')
cliParser.add_argument('indivFileName', metavar='indivFileName', type=str, help='pipe for incoming individual genomes')
cliParser.add_argument('evalsFileName', metavar='evalsFileName', type=str, help='pipe for outgoing individual evaluations')
cliArgs = cliParser.parse_args()

while True:
	genomeStrs = read(cliArgs.indivFileName)
	genomes = map(parseGenome, genomeStrs)
	evals = map(evaluateGenome, genomes)
	evalStrs = map(evalToStr, evals)
	write(cliArgs.evalsFileName, evalStrs)
