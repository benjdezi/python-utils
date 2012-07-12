'''
Created on Feb 21, 2012

@requires:amqplib (pip install amqplib)
@author: Benjamin Dezile
'''

from amqplib import client_0_8 as amqp
import traceback
import json
import re

DEFAULT_USER = "guest"
DEFAULT_PWD = "guest"
DEFAULT_EXCHANGE_TYPE = "topic"
SHUTDOWN = "shutdown"
ALL_PATTERN = "*"

class AMQ:
    ''' RabbitMQ Wrapper. 
    
    Will consume or publish messages from/to a given
    exchange and queue on the RabbitMQ instance (defined in config).
     
    Can act either as a consumer or a publisher, depending 
    on whether a message handler is provided at initialization time.
    '''
    
    verbose = True
    
    def __init__(self, config, queue=None, message_handler=None):
        ''' Create a new wrapper instance
        config:             Config map
        queue:              Queue to listen from
        message_handler:    Method to handle incoming messages
        '''
        
        self.host = config.get('host', None)
        self.port = config.get('port', None)
        self.exchange = config.get('exchange', None)
        self.user = config.get('user', DEFAULT_USER)
        self.pwd = config.get('password', DEFAULT_PWD)
        
        if not self.host or not self.exchange:
            raise Exception('Host and exchange required, none found')
        
        self.queue_name = queue
        self.message_handler = message_handler
        self.is_consumer = (message_handler is not None)
        self.shutdown_signal = SHUTDOWN
        self.publish_properties = { "content_type": "text/plain", "delivery_mode": 1 }
        self.queue_exists = False
        
        self.conn_parameters = {"host": self.host,
                                "userid": self.user,
                                "password": self.pwd,
                                "virtual_host": "/",
                                "insist": False}
    
    @classmethod
    def enable_verbose(cls, is_enabled=True):
        ''' Enable or disable verbose mode '''
        cls.verbose = is_enabled
        
    def _verbose(self, msg):
        ''' Print out a give message '''
        if AMQ.verbose is True:
            print msg
    
    def connect(self):
        ''' Establish connection to the RabbitMQ server '''
        self.connection = amqp.Connection(self.host, self.user, self.pwd)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(self.exchange, DEFAULT_EXCHANGE_TYPE, durable=True)
        self.on = True
        self._verbose("Connected to RabbitMQ @ %s:%d as \"%s\"" % (self.host, self.port, self.user))

    def publish(self, message, routing_key):
        ''' Publish a given message 
        message:        Message content (string or JSON-compatiable object)
        routing_key:    Associated publication key
        '''
        
        msg_data = json.dumps(message, False, False) if type(message) not in [str, unicode] else message
        msg = amqp.Message(msg_data, **self.publish_properties)
        
        self.channel.basic_publish(msg, self.exchange, routing_key)
    
    def _on_message_received(self, msg):
        ''' Internally called whenever a new message is received '''
        if not msg:
            return
        if msg.body == self.shutdown_signal:
            # Shutdown
            self._verbose("Received shutdown signal")
            self.channel.basic_ack(msg.delivery_tag)
            self.close(msg.consumer_tag)
        else:
            try:
                if not self.routing_key_pattern.match(msg.routing_key):
                    # Wrong delivery, skip without ack'ing
                    return
                params = { 'key': msg.routing_key, 'tag': msg.delivery_tag }
                self.message_handler(msg.body, **params)
                self.channel.basic_ack(msg.delivery_tag)
            except Exception, e:
                self._verbose("Error while handling message: %s" % e)
                traceback.print_stack()
    
    def monitor(self, routing_key=None):
        ''' Start monitor for incoming message from the previously specified queue.
        This method blocks until this instance is terminated or a shutdown signal is received.
        routing_key:    Key to listen for
        '''
        
        if not self.message_handler:
            raise Exception("No message handler provided")
        
        if not routing_key:
            routing_key = ALL_PATTERN
        
        if not self.queue_exists:
            self.channel.queue_declare(self.queue_name, durable=True, auto_delete=False)
            self.channel.queue_bind(self.queue_name, self.exchange, routing_key)
            self._verbose("Declared queue %s" % self.queue_name)
            
        self.routing_key = routing_key
        self.routing_key_pattern = re.compile(self.routing_key)
        self.channel.basic_consume(self.queue_name, callback=self._on_message_received)
        self._verbose("Started consuming %s from %s" % (routing_key, self.queue_name))
        
        # Consumption loop
        while True:
            try:
                self.channel.wait()
            except Exception, e:
                if self.on:
                    self._verbose("Error while waiting for messages: %s" % e)
                    traceback.print_stack()
                else:
                    break
    
    def close(self, consumer_tag=None):
        ''' Terminate the connection to the server and any active listening loop '''
        self.on = False
        if consumer_tag:
            self.channel.basic_cancel(consumer_tag)
        self.channel.close()
        self.connection.close()
        self._verbose("Closed connection to RabbitMQ @ %s" % self.host)

