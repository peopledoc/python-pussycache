"""
Implement a base CacheBackend API.

>>> from pussycache.cache.redis_backend import RedisCacheBackend
>>> cache = RedisCacheBackend(100)
>>> cache.set('my_key', 'hello, world!', 3)
>>> cache.get('my_key')
'hello, world!'
>>> import time
>>> time.sleep(3)
>>> cache.get('my_key')

>>> cache.get('my_key', 'has expired')
'has expired'
>>> cache.set('add_key', 'Initial value')
>>> cache.add('add_key', 'New value')
>>> cache.get('add_key')
'Initial value'
>>> cache.add('anotherkey', 'my key')
>>> cache.get('anotherkey')
'my key'
>>> cache.delete('add_key')

>>> cache.get('add_key')

>>> cache.delete('add_key')

>>> cache.set("hello", "world")
>>> cache.clear()

>>> cache.get("hello")

>>> cache.set_many({'a': 1, 'b': 2, 'c': 3})
>>> cache.get_many(['a', 'b', 'c'])['a']
1
>>> cache.delete_many(['a', 'b', 'c'])
>>> cache.get('a')

>>> cache.clear()

"""
try:
    import redis
except ImportError:
    raise ImportError("You need to get a running instance of redis-server \
and the python redis connector (eg: pip install redis) to use this backend")

import pickle
pickle.DEFAULT_PROTOCOL = 2
from pussycache.cache import BaseCacheBackend


class RedisCacheBackend(BaseCacheBackend):
    """
    Redis cache implementation
    """
    def __init__(self, timeout, host='localhost', port=6379, db=0):
        self.db = redis.StrictRedis(host=host, port=port, db=db)
        self.timeout = timeout

    def clear(self):
        self.db.flushdb()

    def set(self, key, value, timeout=None):
        self.db.set(key, pickle.dumps({"value": value}))
        self.db.expire(key, timeout or self.timeout)

    def get(self, key, default_value=None):
        try:
            value = pickle.loads(self.db.get(key))
        except TypeError:
            return default_value or None
        return value["value"]

    def delete(self, key):
        """Remove a key/value from the store """
        self.db.delete(key)

    def add(self, key, value, timeout=None):
        """Add a key/value to the store unless this key already exists """
        if not self.get(key):
            self.set(key, value, timeout=timeout)

    def set_many(self, valuesdict, timeout=None):
        for k, v in valuesdict.items():
            self.set(k, v, timeout=timeout)

    def get_many(self, keys, timeout=None):
        response = {}
        for elem in keys:
            response[elem] = self.get(elem)
        return response

    def delete_many(self, keys):
        if keys:
            self.db.delete(*keys)
