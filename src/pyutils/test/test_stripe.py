'''
Created on Jun 29, 2012

@author: Benjamin Dezile
'''

from pyutils.lib.unit_test import TestSuite, test_case
from pyutils.api.stripe import StripeAPI, StripeCard

class TestStripe(TestSuite):
    ''' Test Stripe API methods '''
    
    def setup(self):
        
        self.card = StripeCard("Mr. Test", "4242424242424242", 12, 2012, 123)
        self.email = "stripe-test@domain.com"
        self.descr = "Test user"
        self.rate = 499
        self.cus_id = None

    @test_case
    def test1_create_new_customer(self):
        ''' Test creating a new customer '''
        self.cus_id = StripeAPI.create_new_customer(self.email, self.descr)
        cus = StripeAPI.get_customer(self.cus_id)
        self.assert_not_none(cus)
        self.assert_equal(cus.id, self.cus_id)

    @test_case
    def test2_set_card(self):
        ''' Test add a new card to an existing customer '''
        token_id = StripeAPI.set_card(self.cus_id, self.card)
        self.assert_not_none(token_id)

    @test_case
    def test3_charge_card(self):
        ''' Test creating a new charge '''
        charge_id = StripeAPI.charge(self.cus_id, self.rate, "Test charge for customer %s" % self.cus_id)
        self.assert_not_none(charge_id)

    @test_case
    def test4_delete_customer(self):
        ''' Test deleting an existing customer '''
        res = StripeAPI.delete_customer(self.cus_id)
        self.assert_true(res)
        self.assert_none(StripeAPI.get_customer(self.cus_id))

if __name__ == "__main__":
    TestStripe().run()
