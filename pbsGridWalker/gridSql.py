import sqlite3
from time import sleep

waitBetweenQueryAttempts = 0.2

def _sqlType(var):
	types = {int: 'INT', float: 'FLOAT', str: 'TEXT'}
	try:
		return types[type(var)]
	except:
		raise ValueError('Conversion of an unsuitable variable type to SQL type attempted. Suitable types: ' + str(types.keys()))

def _sqlStr(var):
	if(type(var) == int or type(var) == float):
		return str(var)
	elif(type(var) == str):
		# TODO Validate the string here
		return '\'' + var + '\''
	else:
		raise ValueError('Conversion of a variable of unsuitable type to SQL converted')

def makeGridTable(grid, dbfilename):
	with sqlite3.connect(dbfilename) as con:
		cur = con.cursor()

		tableDesc = 'Grid(id INT PRIMARY KEY'
		examplePoint = grid[0]
		paramNames = examplePoint.keys()
		for paramName in paramNames:
			tableDesc += ', ' + paramName + ' ' + _sqlType(examplePoint[paramName]) # TODO paramName is not validated!
		tableDesc += ')'
		cur.execute('CREATE TABLE ' + tableDesc + ';')

		for i,point in enumerate(grid):
			vstrs = [ str(i) ] + [ _sqlStr(point[paramName]) for paramName in paramNames ]
			cur.execute('INSERT INTO Grid VALUES (' + ', '.join(vstrs) + ');')

def gridIdsFromSqlite(dbfilename):
	with sqlite3.connect(dbfilename) as con:
		cur = con.cursor()
		cur.execute('SELECT id FROM Grid;')
		idTuples = cur.fetchall()
	return [ id for id, in idTuples ]

def makeGridQueueTable(dbfilename, passes=1):
	ids = gridIdsFromSqlite(dbfilename)
	with sqlite3.connect(dbfilename) as con:
		cur = con.cursor()
		cur.execute('PRAGMA foreign_keys=ON;')
		cur.execute('CREATE TABLE GridQueue(id INT, passesRequested INT, passesDone INT, passesFailed INT, inWorks BOOL, FOREIGN KEY(id) REFERENCES Grid(id));')
		for id in ids:
			cur.execute('INSERT INTO GridQueue VALUES ({}, {}, 0, 0, 0);'.format(id, passes))

def _executeQueryInExclusiveMode(dbfilename, executor):
	'''Executes a callable executor(con) on a connection to the database in exclusive mode'''
	# Courtesy of hops: http://stackoverflow.com/questions/9070369/locking-a-sqlite3-database-in-python-re-asking-for-clarification/12848059#12848059
	for t in range(100):
		try:
			con = sqlite3.connect(dbfilename)
			con.isolation_level = 'EXCLUSIVE'
			con.execute('BEGIN EXCLUSIVE')
			# Exclusive access starts here. Nothing else can r/w the db, do your magic here.
			retval = executor(con)
			con.commit()
			con.close()
			return retval
		except sqlite3.OperationalError as oe:
			print('Warning: operational error occured while accessing the database in exclusive mode, retrying in {} seconds (attempt {})'.format(waitBetweenQueryAttempts, t))
			sleep(waitBetweenQueryAttempts)
	return None

def requestPointFromGridQueue(dbfilename):
	'''Finds a point that is neither worked upon nor done, marks it as worked upon
	   and returns the parameter dictionary. If the point is not found, None is
	   returned.
	'''
	def requester(con):
		con.text_factory = str
		cur = con.cursor()
		cur.execute('SELECT id, passesDone FROM GridQueue WHERE NOT inWorks AND passesRequested > passesDone LIMIT 1;')
		pointIdList = cur.fetchall()
		if len(pointIdList) == 1: # If there is still a point that hasn't been processed
			pointId, passesDone = pointIdList[0]
			curPass = passesDone + 1
			# mark it as being in works
			cur.execute('UPDATE GridQueue SET inWorks=1 WHERE id={};'.format(pointId))
			# fetch and return the grid parameters
			cur.execute('SELECT * FROM Grid WHERE id={};'.format(pointId))
			vals = cur.fetchall()
			dict = {}
			for idx, col in enumerate(cur.description):
				dict[col[0]] = vals[0][idx]
			id = dict.pop('id')
			return id, curPass, dict
		elif len(pointIdList) == 0:
			return None
		else:
			print('WARNING! SELECT query with LIMIT 1 returned more than one result. Something is very, very wrong.')
	return _executeQueryInExclusiveMode(dbfilename, requester)

def reportSuccessOnPoint(dbfilename, id):
	def reporter(con):
		cur = con.cursor()
		cur.execute('UPDATE GridQueue SET inWorks=0, passesDone=passesDone+1 WHERE id={};'.format(id))
	_executeQueryInExclusiveMode(dbfilename, reporter)

def reportFailureOnPoint(dbfilename, id):
	def reporter(con):
		cur = con.cursor()
		cur.execute('UPDATE GridQueue SET inWorks=0, passesFailed=passesFailed+1 WHERE id={};'.format(id))
	_executeQueryInExclusiveMode(dbfilename, reporter)

def _executeQueryPersistently(dbfilename, query):
	for t in range(100):
		try:
			with sqlite3.connect(dbfilename) as con:
				cur = con.cursor()
				cur.execute(query)
				return cur.fetchall()
		except sqlite3.OperationalError as oe:
			print('Warning: operational error occured while executing the query "{}" persistently, retrying in {} seconds (attempt {})'.format(query, waitBetweenQueryAttempts, t))
			sleep(waitBetweenQueryAttempts)
	print('Error: couldnt execute a persistent query "{}" after 100 attempts, giving up'.format(query))
	return None

def checkForCompletion(dbfilename):
	ids = _executeQueryPersistently(dbfilename, 'SELECT id FROM GridQueue WHERE passesDone<passesRequested;')
	return len(ids) == 0

def checkForUntreatedPoints(dbfilename):
	'''A point is considered untreated if it has not reached the required number of passes and is not in works or failed'''
	ids = _executeQueryPersistently(dbfilename, 'SELECT id FROM GridQueue WHERE passesDone<passesRequested AND NOT inWorks AND passesFailed=0;')
	return len(ids) == 0

def numFailures(dbfilename):
	failuresQueryOutput = _executeQueryPersistently(dbfilename, 'SELECT sum(passesFailed) FROM GridQueue;')
	if len(failuresQueryOutput) == 0:
		return 0
	else:
		sum, = failuresQueryOutput[0]
		return sum

def resetInProgressPoints(dbfilename):
	with sqlite3.connect(dbfilename) as con:
		cur = con.cursor()
		cur.execute('UPDATE GridQueue SET inWorks=0,passesDone=0 WHERE inWorks=1;')

def resetFailedPoints(dbfilename):
	with sqlite3.connect(dbfilename) as con:
		cur = con.cursor()
		cur.execute('UPDATE GridQueue SET passesFailed=0,passesDone=0 WHERE passesFailed=1;')

def resetDatabase(dbfilename):
	resetInProgressPoints(dbfilename)
	resetFailedPoints(dbfilename)
