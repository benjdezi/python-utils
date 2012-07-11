'''
Created on Feb 23, 2012

@author: Benjamin Dezile
'''

from subprocess import call
import uuid
import os

class Mailer:
    ''' Mailgun wrapper '''
    
    verbose = True
    api_key = None
    send_url = None
    
    @classmethod
    def init(cls, api_key, send_url, verbose=True):
        ''' Initialize the mailer '''
        cls.verbose = verbose
        cls.api_key = api_key
        cls.send_url = send_url
    
    @classmethod
    def _verbose(cls, msg):
        ''' Print out a message '''
        if cls.verbose is True:
            print msg
    
    @classmethod
    def send(cls, msg, subject, to_address, from_address):
        ''' Send the given message via email to the specified adress 
        msg:               Message content
        subject:           Message subject (optional)
        to_address:        Recipient's email address
        from_address:      Sender's email address
        '''
        
        if not msg or not to_address or not from_address:
            raise ValueError("Missing or invalid parameters")
        
        tmp_filepath = os.path.join('tmp', "%s.mailgun.out" % uuid.uuid4())
        cli_params = ["curl", "-s", "-k", "--user",
                      "api:%s" % cls.api_key,
                      cls.send_url,
                      "-F", "from=%s" % from_address,
                      "-F", "to=%s" % to_address,
                      "-F", "subject=%s" % (subject.replace("'", "\'") if subject else ""),
                      "-F", "text=" % msg.replace("'", "\'"), 
                      ">", tmp_filepath]
        fp = None
        try:
            
            fp = open(tmp_filepath, 'w+')
            ret_val = call(cli_params, stdout=fp, stderr=fp)
            fp.close()
            
            fp = open(tmp_filepath, 'r')
            resp = fp.read()
            fp.close()
            
            cls._verbose("Send email \"%s\" to %s: return = %s, response = %s" % (subject, to_address, ret_val, resp.replace("\n", "")))
        finally:
            if fp: 
                fp.close()
            try: 
                os.remove(tmp_filepath) 
            except: 
                pass

