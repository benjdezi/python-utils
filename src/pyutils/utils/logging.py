'''
Created on Feb 20, 2012

@author: Benjamin Dezile
'''

from datetime import datetime
import traceback

class Logger:
	''' General logger '''
	
	LOG_LEVEL_ERROR = 0
	LOG_LEVEL_WARN = 1
	LOG_LEVEL_INFO = 2
	LOG_LEVEL_DEBUG = 3
	LOG_LEVEL_TRACE = 4
	LOG_LEVEL_ALL = 5
	LEVEL_NAMES = ["Error", "Warning", "Info", "Debug", "Trace"]
	
	options = { 'level': 5 }

	@classmethod
	def init(cls, **options):
		''' Initialize logging with the given options '''
		cls.options = options
	
	@classmethod
	def set_options(cls, **new_options):
		''' Set new option values '''
		for k in new_options.keys():
			cls.options[k] = new_options[k]
			
	@classmethod
	def set_level(cls, new_level):
		''' Set the logging level '''
		cls.options['level'] = new_level
			
	@classmethod	
	def _log(cls, level, msg):
		''' Log a message for a given logging level '''
		if cls.options['level'] >= level:
			print "%s - %s: %s" % (datetime.utcnow(), cls.LEVEL_NAMES[level], msg)

	@classmethod
	def info(cls, msg):
		''' Log an information message '''
		cls._log(Logger.LOG_LEVEL_INFO, msg)

	@classmethod
	def error(cls, msg, err = None):
		''' Log an error message '''
		if err:
			msg = "%s (%s)" % (msg, err) 
		cls._log(cls.LOG_LEVEL_ERROR, msg)
		if err:
			traceback.print_stack()

	@classmethod
	def warn(cls, msg):
		''' Log a warning message '''
		cls._log(Logger.LOG_LEVEL_WARN, msg)

	@classmethod
	def debug(cls, msg):
		''' Log a debug message '''
		cls._log(Logger.LOG_LEVEL_DEBUG, msg)

	@classmethod
	def trace(cls, msg):
		''' Log a tracing message '''
		cls._log(Logger.LOG_LEVEL_TRACE, msg)

