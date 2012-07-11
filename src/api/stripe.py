'''
Created on Feb 28, 2012

@author: Benjamin Dezile
'''

from utils.logging import Logger
from utils.config import Config
import stripe

DEFAULT_CURRENCY = "usd"

class StripeCard:
    ''' Stripe credit card '''
    
    def __init__(self, number, month, year, name=None, cvc=None):
        ''' Create a new card 
        number: Card number (string, no separator)
        month: Expiration month (2 digits)
        year: Expiration year (4 digits)
        name: Owner's name
        cvc: Security code 
        '''
        self.name = name
        self.number = number
        self.month= month
        self.year = year
        self.cvc = cvc
        
    def to_dict(self):
        ''' Export this card's parameters to a dictionary '''
        return { 'name': self.name, 
                'number': self.number, 
                'exp_month': self.month, 
                'exp_year': self.year, 
                'cvc': self.cvc }


class StripeAPI:
    ''' Stripe API wrapper '''
    
    instance = None
    
    def __init__(self, config=None):
        ''' Create a new API wrapper '''
        if StripeAPI.instance: 
            raise Exception("Singleton already initialized")
        self.config = Config.get("stripe")
        if config and type(config) is dict:
            for k in config.keys():
                self.config[k] = config[k] 
        stripe.api_key = self.config['secret']
        StripeAPI.instance = self
        
    @classmethod
    def create_new_customer(cls, email, description=None):
        ''' Create a new customer 
        email:            Associated email address
        description:      Optional description
        '''
        if not description:
            description = email
        # Create new customer
        cus = stripe.Customer.create(email=email, description=description)
        Logger.info("Created new Stripe customer [%s] for " % (cus.id, email))
        return cus.id
    
    @classmethod
    def delete_customer(cls, cus_id):
        ''' Delete the customer associated with a given user 
        cus_id:    Customer id
        '''
        # Delete customer
        cus = cls._get_customer(cus_id)
        resp = cus.delete()
        if resp.deleted:
            Logger.info("Deleted customer %s" % cus.id)
            return True
        return False
    
    @classmethod
    def _get_customer(cls, cus_id):
        ''' Get a customer '''
        if not cus_id:
            raise ValueError('No customer id provided')
        return stripe.Customer.retrieve(cus_id)
    
    @classmethod
    def set_card(cls, cus_id, card):
        ''' Set a card for a given customer 
        cus_id:     Customer to set the card for
        card:       Card object 
        '''
        
        if not card or type(card) is not StripeCard:
            raise TypeError('Card must be a valid StripeCard object')
        
        # Create new token
        token = stripe.Token.create(card=card.to_dict(), currency=DEFAULT_CURRENCY)
        
        # Update customer info
        cus = cls._getCustomer(cus_id)
        cus.card = token.id
        cus.save()

        Logger.info("Set card [%s] for user %s" % (token.id, cus_id))
        return token.id
    
    @classmethod
    def charge(cls, cus_id, amount_cents, description=None):
        ''' Create a new charge for a customer 
        cus_id:            Customer to be charged
        amount_cents:      Amount to be charged in cents
        description:       Optional description
        '''
        
        # Build request parameters
        params = {'amount': int(amount_cents * 100),
                  'currency': DEFAULT_CURRENCY,
                  'customer': cus_id,
                  'description': description }
        # Create new charge
        charge = stripe.Charge.create(**params)
        if charge.paid:
            Logger.info("Charged [%s] customer %s for %f %s" % (charge.id, cus_id, amount_cents, charge.currency.upper()))
            return charge.id
        else:
            raise Exception("Could not charge customer %s, response = %s" % (cus_id, charge))
        

if not StripeAPI.instance:
    StripeAPI()