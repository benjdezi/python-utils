'''
Created on Feb 24, 2012

@requires: redis (pip install redis)
@author: Benjamin Dezile
'''

from pyutils.utils.config import Config
from cStringIO import StringIO
import redis
import uuid

class Cache:
    ''' Caching wrapper built on top Redis
    
    Cacheable types:
     - Dictionaries
     - Sets, Lists
     - Strings, Numbers, Booleans
    
    '''

    NS_REQUEST = "request"
    NS_WEB_PAGE = "webpage"
    NS_GEO_LOC = "geo"
    NS_PREFIXES = {"request": "req_",
                   "webpage": "web_",
                   "geo": "geo_"}
    
    REDIS_TYPE_NONE = "none"
    REDIS_TYPE_HASH = "hash"
    REDIS_TYPE_STR = "string"
    REDIS_TYPE_LIST = "list"
    REDIS_TYPE_SET = "set"
    REDIS_TYPE_SORTED_SET = "zset"
    KEY_DEFAULT_TTL = 3600
    DEFAULT_PORT = 6379
    DEFAULT_HOST = Config.get("redis", "host")
    
    instance = None
    
    def __init__(self, **kw):
        self.host = kw.get('host', Cache.DEFAULT_HOST)
        self.port = kw.get('port', Cache.DEFAULT_PORT)
        self.db_index = kw.get('db', 0)
        self.redis = redis.StrictRedis(host=self.host, port=self.port)
        # XXX: Not implemented in lib yet
        #if self.db_index > 0:
        #    self.redis.select(self.db_index)
        self.instance = self
    
    @classmethod
    def make_ns_key(cls, ns, controller_name, action_name, params=None):
        ''' Build a namespaced cache key '''
        buf = StringIO()
        buf.write("%s%s%s" % (cls.NS_PREFIXES[ns], controller_name, "_" + action_name if action_name else ""))
        if params:
            buf.write("?")
            for k in params:
                if params[k]:
                    buf.write(k)
                    buf.write("=")
                    buf.write(str(params[k]))
                    buf.write("&")
        cache_key = buf.getvalue().rstrip("&")
        buf.close()
        return cache_key
    
    @classmethod
    def get_instance(cls, **kw):
        ''' Return the cache instance '''
        return Cache(**kw)
        
    @classmethod
    def put(cls, key, obj, ttl=None, **options):
        ''' Put a new value in cache 
        key:        Storage key
        obj:        Value
        ttl:        Time to live in seconds (None = Infinity)
        options:    Additional options
                    - sorted: whether it's a set of sorted values
        ''' 
        r = cls.instance.redis
        t = type(obj)
        tc = r.type(key)
        
        if t == str or t == unicode:
            if tc == cls.REDIS_TYPE_HASH:
                # Add a string to a hash
                r.hmset(key, obj)
            elif tc == cls.REDIS_TYPE_LIST:
                # Add a string to a list
                r.rpush(key, obj)
            elif tc == cls.REDIS_TYPE_SET:
                # Add a string to a set
                r.sadd(key, obj)
            else:
                # Set a string key
                r.set(key, obj)
        elif t == dict:
            if options.get('sorted', False) is True:
                # Add values to a sorted set
                r.zadd(key, **obj)
            else:
                # Add values to a hash
                r.hmset(key, obj)
        elif t == list:
            # Add values to a list
            for x in obj: 
                r.rpush(key, x)
        elif t == set:
            # Add values to a set
            r.sadd(key, *obj)
        else:
            raise ValueError("Unsupported type of cache object: " + str(type(obj)))
        
        if ttl:
            r.expire(key, ttl)
    
    @classmethod
    def keys(cls, pattern):
        ''' Return the list of keys matching the given pattern '''
        r = cls.instance.redis
        return r.keys(pattern)
    
    @classmethod
    def get(cls, key, **options):
        ''' Get a cache value, None if not found 
        key:         Key to read from
        options:     Additional options
                     - range: range of indexes to get from a sorted set
                     - score_range: same but with scores
                     - no_eval: return data as is if True
        '''
        
        r = cls.instance.redis
        t = r.type(key)
        no_eval = options.get("no_eval", False)
        
        if t == cls.REDIS_TYPE_NONE:
            
            # None
            return None
        
        elif t == cls.REDIS_TYPE_HASH:
            
            # Hash
            d = r.hgetall(key)
            if d:
                for k in d:
                    d[k] = cls._eval(d[k])
                return d
            
        elif t == cls.REDIS_TYPE_STR:
            
            # String
            s = r.get(key)
            return cls._eval(s) if s and not no_eval else s
            
        elif t == cls.REDIS_TYPE_LIST:
            
            # List
            l = r.lrange(key, 0, -1)
            if l:
                for i in range(0, len(l)):
                    l[i] = cls._eval(l[i])
                return l
            
        elif t == cls.REDIS_TYPE_SET:
            
            # Set
            s1 = r.smembers(key)
            if s1:
                s2 = set()
                for x in s1:
                    s2.add(cls._eval(x))
                return s2
            
        elif t == cls.REDIS_TYPE_SORTED_SET:
            
            # Sorted set
            rng = options.get('range', (0, -1))
            srng = options.get('score_range', None)
            if srng:
                return r.zrangebyscore(key, *srng)
            elif rng:
                return r.zrange(key, *rng)
            else:
                raise ValueError('No range info found')
            
        else:
            
            # Unknown
            raise ValueError('Unknown key type:' + str(t)) 
    
    @classmethod
    def _eval(cls, v):
        ''' Evaluate a given value '''
        try:
            return eval(v)
        except:
            return v
    
    @classmethod
    def has(cls, key):
        ''' Return whether a key exists in cache '''
        return cls.instance.redis.exists(key)
    
    @classmethod
    def remove(cls, key_pattern, get_val=True):
        ''' Remove a value from cache 
        key:      Storage key pattern
        get_val:  Whether to return the old value(s)   
        '''
        r = cls.instance.redis
        keys = r.keys(key_pattern) 
        
        if len(keys) == 1:
            val = cls.get(keys[0]) if get_val else None
            r.delete(keys[0])
            return val
        elif len(keys) > 1:
            vals = list()
            for key in keys:
                if get_val:
                    vals.append(cls.get(key))
                r.delete(key)
            return vals

    @classmethod
    def size(cls, key=None):
        ''' Return the number of entries in cache 
        or the number of entries in a given key 
        '''
        if not key:
            return cls.instance.redis.dbsize()
        else:
            r = cls.instance.redis
            t = r.type(key)
            if t == cls.REDIS_TYPE_HASH:
                return r.hlen(key)
            elif t == cls.REDIS_TYPE_LIST:
                return r.llen(key)
            elif t == cls.REDIS_TYPE_SET:
                return r.scard(key)
            elif t == cls.REDIS_TYPE_SORTED_SET:
                return r.zcard(key)
            else:
                return -1

    @classmethod
    def flush(cls):
        ''' Remove all cache entries '''
        return cls.instance.redis.flushdb()
    
    @classmethod
    def remove_from(cls, key, value):
        ''' Remove a value from a cache entry (if applicable).
        Only works with hash or set.
        key:        Key to remove from
        value:      Value to be removed
         '''
        
        r = cls.instance.redis
        t = r.type(key)
        
        if t == cls.REDIS_TYPE_SET:
            # Remove from a set
            return r.srem(key, value)
        elif t == cls.REDIS_TYPE_SORTED_SET:
            # Remove from a sorted set
            return r.zrem(key, value)
        elif t == cls.REDIS_TYPE_HASH:
            # Remove from a hash
            return r.hdel(key, value)
        else:
            raise ValueError("%s be a set or hash" % key)
    
    @classmethod
    def _get_rnd_key(cls, base=None):
        ''' Generate a random key '''
        return "%s%s" % (base if base else "", uuid.uuid4())
    
    @classmethod
    def union(cls, *keys, **kw):
        ''' Compute the union of two sets.
        Return the union set if not in-place, (res_key, res_card) otherwise.
        Always in-place for sorted sets.
        '''
        in_place = kw.get('inplace', False)
        r = cls.instance.redis
        allowed_types = (cls.REDIS_TYPE_NONE, cls.REDIS_TYPE_SET, cls.REDIS_TYPE_SORTED_SET)
        for key in keys:
            if r.type(key) not in allowed_types:
                raise ValueError("%s must be a set" % key)
        
        if r.type(keys[0]) == cls.REDIS_TYPE_SORTED_SET:
            # Sorted sets
            tmp_key = cls._get_rnd_key("union-")
            n = r.zunionstore(tmp_key, keys)
            r.expire(tmp_key, cls.KEY_DEFAULT_TTL)
            return (tmp_key, n)
        elif not in_place:
            # Non-sorted sets
            return r.sunion(*keys)
        else:
            # Stored non-sorted sets
            tmp_key = cls._get_rnd_key("union-")
            n = r.sunionstore(tmp_key, *keys)
            r.expire(tmp_key, cls.KEY_DEFAULT_TTL)
            return (tmp_key, n)
            
    @classmethod
    def inter(cls, *keys, **kw):
        ''' Compute the intersection of two sets. 
        Return the union set if not in-place, (res_key, res_card) otherwise.
        '''
        in_place = kw.get('inplace', False)
        r = cls.instance.redis
        allowed_types = (cls.REDIS_TYPE_NONE, cls.REDIS_TYPE_SET, cls.REDIS_TYPE_SORTED_SET)
        for key in keys:
            t = r.type(key)
            if t not in allowed_types:
                raise ValueError("%s must be a set" % key)
        
        if r.type(keys[0]) == cls.REDIS_TYPE_SORTED_SET:
            # Sorted sets
            tmp_key = cls._get_rnd_key("inter-")
            n = r.zinterstore(tmp_key, keys)
            r.expire(tmp_key, cls.KEY_DEFAULT_TTL)
            return (tmp_key, n) 
        elif not in_place:
            # Non-sorted sets
            return r.sinter(*keys)
        else:
            # Stored non-sorted sets
            tmp_key = cls._get_rnd_key("inter-")
            n = r.sinterstore(tmp_key, *keys)
            r.expire(tmp_key, cls.KEY_DEFAULT_TTL)
            return (tmp_key, n)

    @classmethod
    def info(cls):
        ''' Get stats about the cache instance '''
        return cls.instance.redis.info()


if not Cache.instance:
    Cache.instance = Cache()
