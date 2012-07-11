'''
Created on Feb 20, 2012

@author: Benjamin Dezile
'''

import yaml
import os

ENV_DEV = "dev"
ENV_STAGING = "staging"
ENV_PROD = "prod"

class ConfigParser:
    ''' Parse config files '''
    
    def __init__(self):
        self.config = dict()
    
    def parse(self, filepath, key = None):
        ''' Parse the given file 
        filepath:     Absolute path to the file to parse
        key:          Key to store config under
        '''
        fp = None
        try:
            fp = open(filepath, 'r')
            m = yaml.load(fp.read())
            if key and not self.config.has_key(key): 
                self.config[key] = dict()
            root = self.config if not key else self.config[key]
            for k in m.keys():
                root[k] = m[k]
            print "Loaded configuration from %s" % filepath
        finally:
            if fp: fp.close()
            
    def get(self):
        ''' Return the last configuration that was parsed '''
        return self.config


class Config:
    ''' Configuration data access '''
    
    config = None
    env = None
        
    @classmethod
    def _eval(cls, val):
        ''' Evaluate an expression if necessary '''
        _val = str(val).strip().lower()
        if _val == "true":
            return True
        if _val == "false":
            return False
        if not _val or _val.find("$") < 0:
            return val
        a = _val.find("${")
        b = _val.find("}", a)
        s = _val[a+2:b]
        parts = s.split(".")
        v = cls.config
        for part in parts:
            v = v.get(part, None)
            if not eval:
                raise Exception("Could not evaluate %s: Not found" % s)
        _val = _val.replace(_val[a:b+1], str(v))
        return cls._eval(_val)
    
    @classmethod
    def get(cls, section, key = None):
        ''' Get a config value 
        section:    Subsection or root key
        key:        Key within the specified section
        '''
        
        if section is None and key is None:
            # Return all
            return cls.config
        
        val = None
        if key is None:
            val = cls.config.get(section, None)
            for k in val:
                val[k] = cls._eval(val[k])
        else:
            sec = cls.config.get(section, None)
            if not sec:
                raise ValueError("Section not found: %s" % section)
            val = sec.get(key, None)
            
        return (cls._eval(val) if type(val) == str else val)
        
    @classmethod
    def is_dev(cls):
        ''' Return True if the current environment is dev '''
        return cls.env == ENV_DEV
    
    @classmethod
    def is_staging(cls):
        ''' Return True if the current environment is staging '''
        return cls.env == ENV_STAGING
    
    @classmethod
    def is_prod(cls):
        ''' Return True if the current environment is prod '''
        return cls.env == ENV_PROD

    @classmethod
    def get_env(cls):
        ''' Return the current environment '''
        return cls.env

    @classmethod
    def get_app_name(cls):
        ''' Return the name of the application '''
        try:
            name = cls.get("application", "name")
            return name.capitalize()
        except ValueError:
            return None

    @classmethod
    def get_version(cls):
        ''' Return the current version of the application '''
        try:
            return cls.get("application", "version")
        except ValueError:
            return None

    @classmethod
    def get_domain(cls):
        ''' Get the root domain name '''
        try:
            return cls.get("application", "domain")
        except ValueError:
            return None
        
    @classmethod
    def get_root_url(cls):
        ''' Return the root url for the web application '''
        app_domain = cls.get_domain()
        app_port = None
        try:
            app_port = cls.get("server", "port")
        except ValueError:
            pass
        return "//%s%s" % (app_domain, (":%s" % app_port if app_port else ""))

    @classmethod
    def init(cls, config_dir=None, config_files=None):
        ''' Initialize configuration 
        config_dir:    Config directory
        config_files:  Config files to be parsed (list or map of file -> namespace key)
        '''
        if not cls.config:
            print "Loading application configuration"
            root = config_dir if config_dir is not None else "."
            reader = ConfigParser()
            try:
                
                # Load config files
                if config_files:
                    # No files, just get all from directory
                    for file_name in os.listdir(root):
                        if file_name.endswith(".yml"):
                            reader.parse(os.path.join(root, file_name))
                elif type(config_files) is list:
                    # List of files
                    for file_name in config_files:
                        reader.parse(os.path.join(root, file_name))
                elif type(config_files) is dict:
                    # Files mapped to namespace keys
                    for file_name in config_files.keys():
                        reader.parse(os.path.join(root, file_name), config_files[file_name])
                        
                # Get environment
                app_config = cls.config.get('application')
                if app_config and app_config.has_key('env'):
                    cls.env = app_config['env']
                        
                print "Loaded configuration"
            except Exception, e:
                print "Error while reading config file: %s" % e
