'''
Created on Feb 23, 2012

@author: Benjamin Dezile
'''

from subprocess import call
import uuid
import json
import os

class Mailer:
    ''' Mailgun wrapper '''
    
    verbose = True
    api_key = None
    send_url = None
    
    def __init__(self, api_key, send_url, verbose=True):
        ''' Initialize the mailer '''
        self.verbose = verbose
        self.api_key = api_key
        self.send_url = send_url
    
    def _verbose(self, msg):
        ''' Print out a message '''
        if self.verbose is True:
            print msg
    
    def send(self, msg, subject, to_addresses, from_address, reply_to=None):
        ''' Send the given message via email to the specified adress 
        msg:               Message content
        subject:           Message subject (optional)
        to_addresses:      List of recipients
        from_address:      Sender's email address
        reply_to:          Address to reply to
        '''
        
        if not msg or not to_addresses or not from_address:
            raise ValueError("Missing or invalid parameters")
        
        tmp_filepath = os.path.join('/tmp', "%s.mailgun.out" % uuid.uuid4())
        cli_params = ["curl", "-s", "-k", "--user", "api:%s" % self.api_key, self.send_url]
        cli_params.append("-F")
        cli_params.append("from=%s" % from_address)
        for to_address in to_addresses:
            cli_params.append("-F")
            cli_params.append("to=%s" % to_address)
        if reply_to:
            cli_params.append("-F")
            cli_params.append("h:reply-to=%s" % reply_to)
        cli_params.append("-F")
        cli_params.append("subject=%s" % (subject.replace("'", "\'") if subject else ""))
        cli_params.append("-F")
        cli_params.append("text=%s" % msg.replace("'", "\'"))
        cli_params.append(">")
        cli_params.append(tmp_filepath)
        
        fp = None
        try:
            
            fp = open(tmp_filepath, 'w+')
            ret_val = call(cli_params, stdout=fp, stderr=fp)
            fp.close()
            
            fp = open(tmp_filepath, 'r')
            resp = fp.read()
            fp.close()
            
            failure = False
            resp = resp.replace("\n", "")
            try:
                resp = json.loads(resp)
                failure = (not resp.has_key("id"))
            except:
                failure = True
            
            if failure:
                raise Exception("Failed to send message (%s)" % resp)
            
            self._verbose("Sent email \"%s\" to %s: return = %s, response = %s" % (subject, to_address, ret_val, resp))
            
            # Success
            return True
            
        finally:
            if fp: 
                fp.close()
            try: 
                os.remove(tmp_filepath) 
            except BaseException: 
                pass

