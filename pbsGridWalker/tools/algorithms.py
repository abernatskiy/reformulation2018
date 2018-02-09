def chunks(l, n):
	'''Yield successive n-sized chunks from l'''
	for i in xrange(0, len(l), n):
		yield l[i:i+n]

def sumOfDicts(a, b, strict=True):
	'''Returns a dictionary which contais all keys and values from both input dictionaries.
     Raises a ValueError when there is a key collision
  '''
	outDict = {}
	outDict.update(a)
	for keyb in b:
		if strict and outDict.has_key(keyb):
			raise ValueError('Key collision when computing the sum of dicts: key {} is present in both dictionaries'.format(keyb))
		outDict[keyb] = b[keyb]
	return outDict

def classifyDict(dict, classifier, safely=True):
	'''{a:1, b:2, c:3, d:4} + {I: [a,b], II: [c]} -> {I: {a:1, b:2}, II: {c:3}}
	   If safely flag is on, will throw ValueError if the first dictionary
	   has any keys unknown to the classifier.
	'''
	from copy import deepcopy
	cdict = deepcopy(dict)
	classified = {}
	for category, catkeys in classifier.items():
		classified[category] = {}
		for catkey in catkeys:
			try:
				classified[category][catkey] = cdict.pop(catkey)
			except KeyError:
				pass
	if safely and len(cdict)>0:
		raise ValueError('Couldn\'t classify some keys: {}. Check your dictionary!'.format(cdict.keys()))
	return classified

def classifyDictWithRegexps(dict, regexpClassifier, safely=True):
	'''{a:1, b:2, c:3, d:4} + {I: [a, regexpb], II: [c]}
     --(iff b matches regexpb)--> {I: {a:1, b:2}, II: {c:3}}
	   If safely flag is on, will throw ValueError if the first dictionary
	   has any keys unknown to the classifier.
	'''
	from copy import deepcopy
	import re
	regexpForNonRegexps = re.compile('^[0-9a-zA-Z]*$')

	cdict = deepcopy(dict)
	classified = {}

	for category, catkeys in regexpClassifier.items():
		classified[category] = {}
		for catkey in catkeys:
			if regexpForNonRegexps.match(catkey):
				try:
					classified[category][catkey] = cdict.pop(catkey)
				except KeyError:
					pass
			else:
				catKeyRegexp = re.compile(catkey)
				matchingKeys = [ cdictKey for cdictKey in cdict.keys() if catKeyRegexp.match(cdictKey) ]
				for mkey in	 matchingKeys:
					classified[category][mkey] = cdict.pop(mkey)
	if safely and len(cdict)>0:
		raise ValueError('Couldn\'t classify some keys: {}. Check your dictionary!'.format(cdict.keys()))
	return classified

def listsIntersect(a, b):
	'''True iff there is at least one element in common between the two (iterable) arguments'''
	return any(i in a for i in b)

def ratioCeil(numerator, denomenator):
	'''Returns ceiling of the ratio of numerator and denumenator'''
	return (numerator+denomenator-1) / denomenator

def splitIntegerRangeIntoStages(beginning, end, stages):
	'''Returns a list of integers where the first integer is beginning,
     the last in end and there are stages-2 approximately equally
     spaced integers between them. Needless to say, stages must be
     a positive integer greater or equal to 2.
  '''
	if stages < 2:
		raise ValueError('Cannot split a range [{}, {}] into less than two ({}) stages'.format(beginning, end, stages))
	out = [beginning]
	for interstages in range(1, stages-1):
		approxPos = float(beginning) + (float(end-beginning)/(stages-1))*float(interstages)
		pos = int(round(approxPos))
		if not out[-1] == pos:
			out.append(pos)
	if not out[-1] == end:
		out.append(end)
	if len(out) != stages:
		print('Couldn\'t split the interval [{}, {}] in {} stages, had to settle for less'.format(beginning, end, stages))
	return out
