import re

def afpr(number, precision=10):
	'''Alignable floating point representation'''
	if number < 0:
		return ('%0.' + str(precision) + 'f') % number
	else:
		return ('%0.' + str(precision+1) + 'f') % number

def translateParametersDictionary(dict, optionalParametersTranslator, requiredParametersTranslator=None):
	translatorFuncs = {'toFloat'  : float,
	                   'toInt'    : int,
	                   'toBool'   : lambda x: x if type(x) is bool else x == 'yes',
	                   'toString' : str} # all translator functions must be projections: f(f(x)) = f(x) for any x
	def translateParamDictInModes(dictionary, translator, allParamsRequired):
		regexpForNonRegexps = re.compile('^[0-9a-zA-Z]*$')
		for convStr, paramNames in translator.iteritems():
			for paramName in paramNames:
				matchCount = 0
				for k in dictionary.keys():
					if regexpForNonRegexps.match(paramName):
						if paramName == k:
							dictionary[k] = translatorFuncs[convStr](dictionary[k])
							matchCount += 1
					elif re.match(paramName, k):
						dictionary[k] = translatorFuncs[convStr](dictionary[k])
						matchCount += 1
				if allParamsRequired and matchCount == 0:
					raise ValueError('Required parameter ' + paramName + ' is missing from the parameter dictionary ' + str(dict) + '. Requirements:\n' + str(requiredParametersTranslator))
		return dictionary
	dict = translateParamDictInModes(dict, requiredParametersTranslator, True)
	return translateParamDictInModes(dict, optionalParametersTranslator, False)

def emptyParametersTranslator():
	return { 'toFloat': set(), 'toInt': set(), 'toBool': set(), 'toString': set() }
