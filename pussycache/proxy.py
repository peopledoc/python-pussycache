"""
This proxy manage cached data from a CacheBackend and fresh data from
a novacoreclient.backend
"""
from inspect import ismethod
from .cache import cachedecorator, invalidator


class BaseProxy(object):
    """
    :param proxied: is the object you want to cache

    :param cache : is a child class of
                         novacoreclient.cache.BaseCacheBackend

    :param cached_methods: is a list of backend methods to be cached

    :param invalidate_methods: is a dict where keys are the methods
                               invalidating the cache, the value a list of
                               methods to be cache invalidated
    """

    def __init__(self, proxied=None, cache=None, cached_methods=None,
                 invalidate_methods=None):

        self._proxied = proxied
        self._cache = cache
        self._cached_methods = cached_methods
        self._invalidate_methods = invalidate_methods

        self.proxify_methods()

    def proxify_methods(self):
        # Cached methods
        for method in self._cached_methods:
            proxied_method = getattr(self._proxied, method)
            if ismethod(proxied_method):
                setattr(self, method,
                        cachedecorator(proxied_method, self._cache))

        # Invalidators methods
        for method in self._invalidate_methods:
            proxied_method = getattr(self._proxied, method)
            if ismethod(proxied_method):
                setattr(self, method, invalidator(
                        proxied_method,
                        self._invalidate_methods, self._cache))

    def __getattr__(self, value):
        return getattr(self._proxied, value)
