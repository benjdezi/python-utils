'''
Created on Jun 29, 2012

@author: Benjamin Dezile
'''

TEST_KEY = "test_key"
TEST_STR = "fdkslfds"
TEST_LIST = [4, "Fds", False, None]
TEST_DICT = { "a":1, "b":"fds", "c":False }
TEST_SET = set(TEST_LIST)
TEST_SORTED_SET = { 'name1':4.0, 'name2':3.0, 'name3':2.0, 'name4':1.0 }

from pyutils.lib.unit_test import TestSuite, test_case
from pyutils.lib.cache import Cache

class TestCache(TestSuite):
    ''' Unit test for Cache '''
    
    def setup(self):
        self.r = Cache.instance.redis
        Cache.flush()
        self.assert_equal(Cache.size(), 0)

    @test_case
    def test1_put_and_get_string(self):
        ''' Test putting/getting strings '''
        key = TEST_KEY + "_str"
        Cache.put(key, TEST_STR)
        obj = Cache.get(key)
        self.assert_not_none(obj)
        self.assert_equal(obj, TEST_STR)
        self.assert_true(Cache.has(key))

    @test_case
    def test2_put_and_get_list(self):
        ''' Test putting/getting lists '''
        key = TEST_KEY + "_list"
        Cache.put(key, TEST_LIST)
        obj = Cache.get(key)
        self.assert_not_none(obj)
        self.assert_equal(obj, TEST_LIST)
        self.assert_true(Cache.has(key))

    @test_case
    def test3_put_and_get_dict(self):
        ''' Test putting/getting dictionaries '''
        key = TEST_KEY + "_dict"
        Cache.put(key, TEST_DICT)
        obj = Cache.get(key)
        self.assert_not_none(obj)
        self.assert_equal(obj, TEST_DICT)
        self.assert_true(Cache.has(key))

    @test_case
    def test4_get_size(self):
        ''' Test getting the cache size '''
        self.assert_equal(Cache.size(), 3)
                
    @test_case
    def test5_remove_from(self):
        ''' Test removing from a set or list '''
        
        key = "testSet"
        Cache.put(key, set([1, 2, 3, 4, 5]))
        self.assert_true(Cache.has(key))
        self.assert_equal(self.r.scard(key), 5)
        Cache.remove_from(key, 3)
        self.assert_equal(self.r.scard(key), 4)
    
    @test_case
    def test6_union(self):
        ''' Test doing the union of two sets '''
        
        key1 = "testSetUnion1"
        key2 = "testSetUnion2"
        N = 10
        s = range(N)
        
        Cache.put(key1, set(s[:N/2]))
        Cache.put(key2, set(s[N/2:]))
        self.assert_true(Cache.has(key1))
        self.assert_equal(self.r.scard(key1), N/2)
        self.assert_true(Cache.has(key2))
        self.assert_equal(self.r.scard(key2), N/2)
        
        u = Cache.union(key1, key2)
        self.assert_not_none(u)
        self.assert_equal(len(u), N)
        for i in u:
            self.assert_in(int(i), s)
        
        (res_key, n) = Cache.union(key1, key2, inplace=True)
        self.assert_equal(n, N)
        self.assert_not_none(res_key)
        self.assert_equal(Cache.size(res_key), n)
        u = Cache.get(res_key)
        for i in u:
            self.assert_in(int(i), s)            
    
    @test_case
    def test7_inter(self):
        ''' Test doing the intersection of two sets '''
        
        key1 = "testSetInter1"
        key2 = "testSetInter2"
        N = 10
        s = range(N)
        inter0 = [5, 6, 7]
        
        Cache.put(key1, set(s[3:8]))
        Cache.put(key2, set(s[5:]))
        self.assert_true(Cache.has(key1))
        self.assert_equal(self.r.scard(key1), N/2)
        self.assert_true(Cache.has(key2))
        self.assert_equal(self.r.scard(key2), N/2)
        
        inter = Cache.inter(key1, key2)
        self.assert_not_none(inter)
        self.assert_equal(len(inter), len(inter0))
        for i in inter:
            self.assert_in(int(i), inter0)
            
        (res_key, n) = Cache.inter(key1, key2, inplace=True)
        self.assert_equal(n, len(inter0))
        self.assert_not_none(res_key)
        self.assert_equal(Cache.size(res_key), n)
        inter = Cache.get(res_key)
        for i in inter:
            self.assert_in(int(i), inter0)

    @test_case
    def test8_sorted_sets(self):
        ''' Test dealing with sorted sets '''
        
        key = "testSortedSet"
        Cache.put(key, TEST_SORTED_SET, sorted=True)
        self.assert_true(Cache.has(key))
        self.assert_equal(Cache.size(key), len(TEST_SORTED_SET))
        self.assert_equal(self.r.type(key), Cache.REDIS_TYPE_SORTED_SET)
        
        items = Cache.get(key, range=(0, -1))
        self.assert_not_none(items)
        self.assert_equal(items, ['name4', 'name3', 'name2', 'name1'])
            
        items = Cache.get(key, score_range=(2.0, 3.0))
        self.assert_not_none(items)
        self.assert_equal(len(items), 2)
        self.assert_equal(items, ['name3', 'name2'])
            
    @test_case
    def test9_keys(self):
        ''' Test getting key listing based on patterns '''
        
        base_key = "test_key_unique_"
        for i in range(10):
            Cache.put("%s%s" % (base_key, i), "1")
        keys = Cache.keys("%s*" % base_key)
        self.assert_not_none(keys)
        self.assert_equal(len(keys), 10)

if __name__ == "__main__":
    TestCache().run()
