'''
Created on Feb 23, 2012

@author: Benjamin Dezile
'''

from subprocess import call
from pyutils.utils.logging import Logger
from pyutils.utils.config import Config
import uuid
import os

API_KEY = Config.get("mailgun", "key")
API_SEND_URL = Config.get("mailgun", "url") + "/koioos.mailgun.org/messages"

class Mailer:
    ''' Mailgun wrapper '''
        
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
                      "api:%s" % API_KEY,
                      API_SEND_URL,
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
            
            Logger.info("Send email \"%s\" to %s: return = %s, response = %s" % (subject, to_address, ret_val, resp.replace("\n", "")))
        finally:
            if fp: 
                fp.close()
            try: 
                os.remove(tmp_filepath) 
            except: 
                pass

