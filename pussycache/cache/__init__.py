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


def cachedecorator(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        instance = method.__self__
        if hasattr(instance, "cache"):
            cache = instance.cache
        else:
            cache = None
        if cache:
            key = "".join((method.__name__, str(args)))
            result = cache.get(key)
            if result is None:
                result = method(*args)
                cache.set(key, result)

            func_list = cache.get("methods_list")
            if func_list is None:
                func_list = []
            if key not in func_list:
                func_list.append(key)
            cache.set("methods_list", func_list, 3600)
            return result
    return wrapper


def invalidator(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        instance = method.im_self
        if hasattr(instance, "invalidator"):
            invalidator = instance.invalidate_meths[method.__name__]
        else:
            invalidator = None
        if invalidator and hasattr(instance, "cache"):
            func_list = instance.cache.get("methods_list")
            if func_list:
                remove_list = []
                for i in invalidator:
                    remove_list += [f for f in func_list if f.startswith(i)]
                instance.cache.delete_many(remove_list)
                func_list = [
                    elem for elem in func_list if elem not in remove_list]
                instance.cache.set("methods_list", func_list)
        result = method(*args)
        return result
    return wrapper


class CacheWrapper(object):
    """
    A mixin decorating children class method with a decorator.


    :param cached_meths: a list of method to be decorated

    :param decorator: the decorator tu use on decorated_meths
    """

    def __init__(self, *args, **kwargs):
        self.cached_meths = kwargs.pop('cached_meths')
        self.cache_decorator = kwargs.pop('cache_decorator')
        self.invalidate_meths = kwargs.pop('invalidate_methods')
        self.invalidator = kwargs.pop('invalidator')
        super(CacheWrapper, self).__init__(*args, **kwargs)

        if self.cached_meths and self.cache_decorator:
            for a in dir(self):
                if not a.startswith("_"):
                    if callable(getattr(self, a)) and\
                            a in self.cached_meths:
                        setattr(self,
                                a,
                                self.cache_decorator(getattr(self, a)))

        if self.invalidate_meths and self.invalidator:
            for a in dir(self):
                if not a.startswith("_"):
                    if callable(getattr(self, a)) and\
                            a in self.invalidate_meths:
                        setattr(self,
                                a,
                                self.invalidator(getattr(self, a)))
