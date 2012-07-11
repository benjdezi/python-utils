'''
Created on Feb 20, 2012

@author: Benjamin Dezile
'''

from datetime import datetime
from utils.config import Config
import traceback
import sys
import os


class Logger:
	''' General logger '''

	LOG_LEVEL_ERROR = 0
	LOG_LEVEL_WARN = 1
	LOG_LEVEL_INFO = 2
	LOG_LEVEL_DEBUG = 3
	LOG_LEVEL_TRACE = 4
	LOG_LEVEL_ALL = 5
	LEVELS = ["Error", "Warning", "Info", "Debug", "Trace", "All"]

	instance = None

	def __init__(self, **params):
		
		self.options = params
		
		level_name = params.get('level', 'ALL')
		if type(level_name) is str:
			self.level = getattr(self, "LOG_LEVEL_%s" % level_name)
		else:
			self.level = int(level_name)
		
		self.stdout = sys.stdout if params.get('stdout', True) else None
		self.stderr = sys.stderr
		
		root_log_dir = Config.get("logging", "root_log_dir")
		log_dir = params.get('log_dir', "")
		log_file = params.get('log_file', None)
		self.base_filepath = os.path.join(root_log_dir, log_dir, log_file) if log_file else None
		
		self.file_pattern = params.get('file_pattern', None)
		self.rotate = params.get('file_rotate', True)
		self.current_file_ext = None 
		self.file = None
		
		self.file = self._get_file()
		
		self.namespace = params.get('namespace', None)
		
		Logger.instance = self

	@classmethod
	def init(cls):
		''' Initialize logging with default configuration '''
		options = Config.get("logging")
		Logger(**options)
		print "Initialized logging [level=%s]" % cls.LEVELS[cls.instance.level]
	
	@classmethod
	def set_options(cls, **params):
		if cls.instance:
			cls.instance.close()
		for k in params.keys():
			v = params[k]
			cls.instance.options[k] = v
		cls.get_instance(**cls.instance.options)
		
	@classmethod
	def get_instance(cls, **params):
		return Logger(**params)
	
	@classmethod
	def set_level(cls, new_level):
		cls.instance.level = new_level
	
	def close(self):
		if self.file:
			self.file.close()
						
	def _get_file(self):
		''' Return the appropriate file object '''
		if self.rotate is True and self.base_filepath and self.file_pattern:
			d = datetime.now()
			year = str(d.year)
			month = ("0" if d.month < 10 else "") + str(d.month) 
			day = ("0" if d.day < 10 else "") + str(d.day)
			hour = ("0" if d.hour < 10 else "") + str(d.hour)
			file_ext = self.file_pattern.replace('yyyy', year).replace('MM', month).replace('dd', day).replace('HH', hour)
			if file_ext != self.current_file_ext:
				# Update file with new extension
				if self.file and not self.file.closed:
					self.file.close()
				self.current_file_ext = file_ext
				full_path = "%s%s" % (self.base_filepath, self.current_file_ext)
				self.file = open(full_path, 'a')
				print "New log file: %s" % full_path
			return self.file
		else:
			return self.file
			
	def log(self, level, msg):
		''' Log a message for a given logging level '''
		line = "%s - %s: %s" % (datetime.utcnow(), level, msg)
		self.write(line)

	def write(self, data):
		''' Log raw data without any additional formatting '''
		line = "%s\n" % data
		if self.stdout:
			# Write to std out
			self.stdout.write(line)
		fp = self._get_file()
		if fp:
			try:
				# Write to file
				fp.write(line)
				fp.flush()
			except Exception, e:
				self.stderr.write("Could not log message: %s\n" % e)

	@classmethod
	def info(cls, msg):
		''' Log an information message '''
		if cls.instance.level >= Logger.LOG_LEVEL_INFO:
			cls.instance.log("INFO", msg)

	@classmethod
	def error(cls, msg, err = None):
		''' Log an error message '''
		if cls.instance.level >= Logger.LOG_LEVEL_ERROR:
			if err:
				msg = msg + (" (" + str(err) + ")" if err else "")
			cls.instance.log("ERROR", msg)
			if err:
				tb = traceback.format_exc()
				Logger.instance.write(tb)

	@classmethod
	def warn(cls, msg):
		''' Log a warning message '''
		if cls.instance.level >= Logger.LOG_LEVEL_WARN:
			cls.instance.log("WARN", msg)

	@classmethod
	def debug(cls, msg):
		''' Log a debug message '''
		if cls.instance.level >= Logger.LOG_LEVEL_DEBUG:
			cls.instance.log("DEBUG", msg)

	@classmethod
	def trace(cls, msg):
		''' Log a tracing message '''
		if cls.instance.level >= Logger.LOG_LEVEL_TRACE:
			cls.instance.log("TRACE", msg)


if not Logger.instance:
	
	# Global logging initialization
	Logger.init()
