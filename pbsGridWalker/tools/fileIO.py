import subprocess
import sys
sys.path.append('..')
import routes
import imp
sysEnv = imp.load_source('sysEnv', routes.sysEnv)

def extractColumn(path, field, offset=0, dtype=float, separator=' '):
	'''Reads a column (field) from a file (path), ignores some lines (offset), then converts every line of the column into dtype and returns results as a list'''
	cutOut = subprocess.check_output([sysEnv.cut, '-d', separator, '-f', str(field), path])
	valStrs = [ s for s in cutOut.split('\n')[offset:] if s != '' ]
	return map(dtype, valStrs)

def writeColumns(listOfLists, filename, separator=' '):
	'''Takes list of lists and writes its contents into a file.
	   Each list within the list of lists becomes a line; each
	   element becomes a column.
	'''
	with open(filename, 'w') as file:
		for list in listOfLists:
			file.write(separator.join(map(str, list)) + '\n')
