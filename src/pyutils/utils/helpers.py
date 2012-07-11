'''
Created on Feb 22, 2012

Global helpers

@author: Benjamin Dezile
'''

import os.path

DEFAULT_ENCODING = 'MacRoman'#'utf-8'

def set_default_encoding(enc=DEFAULT_ENCODING):
    ''' Set the system default encoding '''
    if 'sys' not in dir():
        import sys
        reload(sys)
    try:
        getattr(sys, 'setdefaultencoding')(enc)
    except AttributeError:
        print "Unable to set default encoding to %s" % enc


##  URL HELPERS  ################################

def url_for_js(file_name):
    ''' Return the full url for a given javascript file '''
    return url_for("js/" + file_name, True) 

def url_for_css(file_name):
    ''' Return the full url for a given stylesheet '''
    return url_for("css/" + file_name, True)

def url_for_img(path):
    ''' Return the full url for a given image '''
    return url_for("img/" + path)

def url_for_page(path, **params):
    ''' Return the full url for a given page '''
    if not path.find("."):
        path += ".html"
    return url_for(path, **params)

def url_for(path, cache_bust=False, **params):
    ''' Return the full url for the given path '''
    from pyutils.utils.config import Config
    url = Config.get_root_url() + "/" + path
    if params:
        url += "?"
        for k in params:
            url += "%s=%s&" % (k, params[k])
    if cache_bust:
        url += ("?" if not params else "") + "v=" + Config.get_version()
    return url


##  PATH HELPERS  ###############################

def get_root_dir():
    ''' Return the project's root directory '''
    this_dir = os.path.dirname(os.path.realpath(__file__))
    parts = this_dir.split("/")
    return "/".join(parts[:-2])

def get_python_dir():
    ''' Return the full path to the python directory '''
    return os.path.join(get_root_dir(), "python")

def get_file_path(rel_path):
    ''' Return the full path to a file '''
    return os.path.join(get_root_dir(), rel_path)

def get_web_dir():
    ''' Return the path to the web directory '''
    return os.path.join(get_root_dir(), "web")
    
def get_data_dir():
    ''' Return the full path to the data directory '''
    return os.path.join(get_web_dir(), "data")
    
def get_web_file_path(rel_path):
    ''' Return the full path to a web file '''
    return os.path.join(get_web_dir(), rel_path)


##  FORMATTING HELPERS  #########################

def camel_to_py_case(s):
    '''  Convert a string from Camel casing to Python casing 
    e.g. OneString to one_string '''
    conv = s[0].lower()
    for c in s[1:]:
        conv += ("_" + c.lower() if c.lower() != c else c)
    return conv

def py_case_to_camel(s):
    ''' Reverse of camel_to_py_case '''
    res = s[0].upper()
    is_next_upper = False
    for c in s[1:]:
        if c == '_':
            is_next_upper = True
        elif is_next_upper:
            is_next_upper = False
            res += c.upper()
        else:
            res += c
    return res

def format_number(n):
    ''' Format a given number for display '''
    n_str = str(n)
    n = len(n_str)
    s = ""
    j = 0
    for i in range(n):
        if j == 3 and n-1-i > 0:
            s = "," + s
            j = 0
        s = n_str[n-1-i] + s
        j += 1
    return s
