"""
This proxy manage cached data from a CacheBackend and fresh data from
a novacoreclient.backend
"""
from .cache import cachedecorator, invalidator, CacheWrapper


class BaseProxy(object):
    """
    :param backend: is the class you want to cache

    :param backend_args: a list or a tuple of args to be passed to backend when
                         instanciated

    :param backend_kwargs: a dict to be passed as **kwargs to backend when
                           instanciated

    :param cache : is a child class of
                         novacoreclient.cache.BaseCacheBackend

    :param cached_methods: is a list of backend methods to be cached

    :param invalidate_methods: is a dict where keys are the methods
                               invalidating the cache, the value a list of
                               methods to be cache invalidated
    """

    def __init__(self, backend=None, backend_args=None, backend_kwargs=None,
                 cache=None, cached_methods=None, invalidate_methods=None):

        self.cache = cache
        backend_kwargs = backend_kwargs or {}
        backend_args = backend_args or ()
        backend_kwargs.update({"cached_meths": cached_methods,
                               "cache_decorator": cachedecorator,
                               "invalidate_methods": invalidate_methods,
                               "invalidator": invalidator})

        self.backend = self.proxify(backend)(*backend_args, **backend_kwargs)
        self.backend.cache = self.cache

    def proxify(self, backend):
        class ProxifiedClass(CacheWrapper, backend):
            pass
        return ProxifiedClass
