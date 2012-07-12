'''
Created on Jul 11, 2012

@author: Benjamin Dezile
'''

from pyutils.lib.unit_test import TestSuite, test_case
from pyutils.api.mailgun import Mailer

TEST_MSG = "This is a test message"
TEST_SUBJECT = "Test"
TEST_TO = "test@domain.com"
TEST_FROM = "tester@domain.com"

class TestMailgun(TestSuite):
    
    def setup(self, api_key, send_url):
        Mailer.init(api_key, send_url)        
    
    @test_case
    def test0_send_email(self):
        ''' Test sending an email '''
        res = Mailer.send(TEST_MSG, TEST_SUBJECT, TEST_TO, TEST_FROM)
        self.assert_true(res)
    
if __name__ == "__main__":
    
    import sys
    
    if len(sys.argv) < 3:
        raise ValueError("Missing API config")
    
    params = { 'api_key': sys.argv[1], 'send_url': sys.argv[2] }
    
    TestMailgun().run(**params)
    