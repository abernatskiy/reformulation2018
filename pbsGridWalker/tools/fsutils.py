import numbers
import shutil
import os

def dictionary2filesystemName(dictionary):
	'''Turns a parameter dictionary into a filesystem-appropriate string,
     ignoring non-numeric values in the dictionary.
     Tip: boolean values are considered numeric.
	'''
	filteredDict = {k: v for k, v in dictionary.iteritems() if isinstance(v, numbers.Number) or isinstance(v, str) }
	if len(filteredDict) == 0:
		if len(dictionary) > 0:
			print('WARNING: Nontrivial numberless dictionary ' + str(dictionary) + ' gets converted into a default string (\'None\') - this may cause some filesystem names to not be unique')
		return 'None'
	else:
		return '_'.join(map(lambda (x, y): x + ':' + str(y), sorted(filteredDict.items())))

def makeDirCarefully(dirname, maxBackups=10):
	if os.path.isdir(dirname):
		print('Directory {} exists, backing it up and creating a new one'.format(dirname))
		for i in xrange(maxBackups):
			curCandidateDir = dirname + '.save' + str(i)
			if not os.path.isdir(curCandidateDir):
				break
			else:
				curCandidateDir = None
		if curCandidateDir is None:
			raise OSError('Too many backups of {} directory (no less than {}). Go clean them up.'.format(dirname, maxBackups))
		else:
			shutil.move(dirname, curCandidateDir)
	elif os.path.exists(dirname):
		raise OSError('Path {} exists, but is not a directory. Go fix it.'.format(dirname))
	os.makedirs(dirname)

def makeUniqueFifo(where, basename):
	path = os.path.join(where, basename + '_pid{}'.format(os.getpid()))
	os.mkfifo(path)
	return path
