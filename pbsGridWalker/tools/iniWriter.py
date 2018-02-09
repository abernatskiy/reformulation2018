import ConfigParser

import algorithms

def write(dict, classifier, outfile):
	'''Classifies parameters supplied with dict into the categories using classifier.
	   The result is written into outfile, using the categories as sections.
	'''
	classified = algorithms.classifyDictWithRegexps(dict, classifier)
	parser = ConfigParser.RawConfigParser()
	parser.optionxform = str
	for category, contents in classified.items():
		parser.add_section(category)
		for key, value in contents.items():
			parser.set(category, key, value)
	with open(outfile, 'wb') as of:
		parser.write(of)
