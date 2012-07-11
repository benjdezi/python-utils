'''
Created on Mar 1, 2012

@author: Benjamin Dezile
'''

import traceback
import inspect
import time


class FailureException(Exception):
    ''' Raised when a test case fails '''
    pass

class SetupException(Exception):
    ''' Raised when setup fails '''
    pass

class TearDownException(Exception):
    ''' Raised when tear down fails '''


def test_case(f):
    ''' Decorator that indicates that a method should be treated as a test case '''
    def new_f(*args, **kw):
        name = "_".join(f.__name__.split("_")[1:])
        print "Running %s" % name
        start_time = time.time()
        try:
            f(*args, **kw)
        except AssertionError, err:
            print "FAILED - Test case %s failed: %s" % (name, err)
            traceback.print_stack()
            raise FailureException()
        dt = round((time.time() - start_time) * 1000, 2)
        print "SUCCESS - Test case %s passed [%s ms]" % (name, dt)
    new_f.is_test_case = True
    new_f.__doc__ = f.__doc__
    return new_f


class TestSuite:
    ''' Unit test suite '''
    
    _reserved = ("setup", "teardown")
    
    def __init__(self, **env_params):
        ''' Create a new instance '''
        self.result_map = dict()
        
    def get_result_map(self):
        ''' Return the result map '''
        return self.result_map
    
    def setup(self):
        ''' Run initialization code before running test cases '''
        pass
    
    def teardown(self):
        ''' Run finalization code after running test cases '''
        pass
    
    def run(self):
        ''' Run the entire set of test cases in this suite '''
        
        print "Running test suite %s" % self.__class__.__name__
        
        success = True
        start_time = time.time()
        
        try: 
            print "Running setup"
            self.setup()
        except Exception, e:
            raise SetupException(e)
        
        for x in inspect.getmembers(self, (inspect.ismethod)):
            if x[0].startswith('test') and x[0] not in self._reserved and hasattr(x[1], 'is_test_case') and x[1].is_test_case == True:
                case_name = "_".join(x[0].split("_")[1:])
                case_success = True
                error = None
                try:
                    x[1]()
                except FailureException:
                    success = False
                    case_success = False
                except BaseException, e:
                    success = False
                    case_success = False
                    error = e
                    print "Error while running test case: %s" % e
                self.result_map[case_name] = (case_success, error)
        dt = round((time.time() - start_time) * 1000, 2)
        
        try:
            print "Running tear down"
            self.teardown()
        except Exception, e:
            raise TearDownException(e)
        
        print "FAILED" if not success else ("PASSED [%s ms]" % dt)
                
    @classmethod
    def assert_in(cls, a, b):
        ''' Assert whether a is in b '''
        if type(b) not in [list, dict, set]:
            raise AssertionError("%s is not iterable" % b)
        if a not in b:
            raise AssertionError("%s is not in %s" % (a, b))

    @classmethod
    def assert_not_in(cls, a, b):
        ''' Assert whether a is not in b '''
        if type(b) not in [list, dict, set]:
            raise AssertionError("%s is not iterable" % b)
        if a in b:
            raise AssertionError("%s is in %s" % (a, b))
    
    @classmethod
    def assert_has_attr(cls, inst, attr_name):
        ''' Assert whether an instance has a given attribute '''
        if inst:
            return hasattr(inst, attr_name)
    
    @classmethod
    def assert_none(cls, obj):
        ''' Assert whether the given object is None '''
        if obj:
            raise AssertionError("%s is not None" % obj)
        
    @classmethod
    def assert_not_none(cls, obj):
        ''' Assert whether the given object is not None '''
        if not obj:
            raise AssertionError("Object is None")
        
    @classmethod
    def assert_equal(cls, a, b):
        ''' Assert whether two objects are equal '''
        if a != b:
            raise AssertionError("%s is not equal to %s" % (a, b))
    
    @classmethod
    def assert_not_equal(cls, a, b):
        ''' Assert whether two objects are not equal '''
        if a == b:
            raise AssertionError("%s is not different from %s" % (a, b))
    
    @classmethod
    def assert_is(cls, a, b):
        ''' Assert whether two objects are the same '''
        if a is not b:
            raise AssertionError("%s is not equal to %s" % (a, b))

    @classmethod
    def assert_is_not(cls, a, b):
        ''' Assert whether two objects are not the same '''
        if a is b:
            raise AssertionError("%s is not different from %s" % (a, b))
    
    @classmethod    
    def assert_is_true(cls, statement):
        ''' Assert whether a statement is true '''
        if not statement:
            raise AssertionError()
        
    @classmethod
    def assert_is_false(cls, statement):
        ''' Assert whether a statement is false '''
        if statement:
            raise AssertionError()
        
    @classmethod
    def assert_gt(cls, a, b):
        ''' Assert whether a > a '''
        if a <= b:
            raise AssertionError("%s is not greater than %s" % (a, b))

    @classmethod
    def assert_lt(cls, a, b):
        ''' Assert whether a < a '''
        if a >= b:
            raise AssertionError("%s is not lesser than %s" % (a, b))

    @classmethod
    def assert_within(self, a, r):
        ''' Assert whether a number is in a given range '''
        if a not in range(*r):
            raise AssertionError("%s is not in %s" % (a, r))

    @classmethod
    def fail(cls, msg=None):
        ''' Fail the current test case '''
        raise AssertionError(msg if msg else "Failed")
