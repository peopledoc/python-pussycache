import calendar
import datetime
from functools import wraps


def get_now_timestamp():
    return calendar.timegm(datetime.datetime.now().utctimetuple())


class BaseCacheBackend(object):
    """ The Base Cache implementation

    Implement a base CacheBackend API.
    >>> from pussycache.cache import BaseCacheBackend
    >>> cache = BaseCacheBackend(100)
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

    def __init__(self, timeout, *args, **kwargs):
        self.timeout = timeout
        self.store = {}

    def clear(self):
        """Clear all the cache"""
        self.store = {}

    def set(self, key, value, timeout=None):
        """Add a key/value to the store """
        expired = get_now_timestamp() + (timeout or self.timeout)
        self.store[key] = {"value": value,
                           "timeout": expired}

    def get(self, key, default_value=None):
        """return the value corresponding to the key or None if
        expired or does not exist """

        try:
            value = self.store[key]
        except KeyError:
            return default_value or None

        if value["timeout"] <= get_now_timestamp():
            self.delete(key)
            return default_value or None
        else:
            return value["value"]

    def delete(self, key):
        """Remove a key/value from the store """
        try:
            self.store.pop(key)
        except KeyError:
            pass  # we do not mind if the key does not exist
        return None

    def add(self, key, value, timeout=None):
        """Add a key/value to the store unless this key already exists """
        val = self.get(key)
        if val is None:
            self.set(key, value, timeout=timeout)

    def set_many(self, valuesdict, timeout=None):
        expired = get_now_timestamp() + (timeout or self.timeout)
        for k, v in valuesdict.items():
            self.store[k] = {"value": v,
                             "timeout": expired}

    def get_many(self, keys, timeout=None):
        response = {}
        for elem in keys:
            response[elem] = self.get(elem)
        return response

    def delete_many(self, keys):
        for elem in keys:
            self.delete(elem)


def cachedecorator(method, cache):

    @wraps(method)
    def wrapper(*args, **kwargs):
        key = "".join((method.__name__, str(args), str(kwargs)))
        result = cache.get(key)
        if result is None:
            result = method(*args, **kwargs)
            cache.set(key, result)

        func_list = cache.get("methods_list")
        if func_list is None:
            func_list = []
        if key not in func_list:
            func_list.append(key)
        cache.set("methods_list", func_list, 3600)
        return result

    return wrapper


def invalidator(method, invalidator_methods, cache):
    @wraps(method)
    def wrapper(*args, **kwargs):
        func_list = cache.get("methods_list")
        invalidated_methods = invalidator_methods[method.__name__]
        if func_list:
            remove_list = []
            for i in invalidated_methods:
                remove_list += [f for f in func_list if f.startswith(i)]
            cache.delete_many(remove_list)
            func_list = [
                elem for elem in func_list if elem not in remove_list]
            cache.set("methods_list", func_list)
        result = method(*args, **kwargs)
        return result
    return wrapper
