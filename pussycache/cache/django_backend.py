"""
A test implementation of Django Cache framework.
from pussycache.cache.django_backend import DjangoCacheBackend
>>> cache = DjangoCacheBackend(100,
...    'django.core.cache.backends.locmem.LocMemCache',
...    'cache-proof-of-concept')
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
False
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

from pussycache.cache import BaseCacheBackend
try:
    from django.conf import settings
except ImportError:
    raise ImportError("You need to install django \
(eg: pip install django) to use this backend")


class DjangoCacheBackend(BaseCacheBackend):
    """
    django cache backend proxy make it possible to use django cache
    backend without Django.
    """
    def __new__(cls, timeout, backend, location, *args, **kwargs):
        caches = {
            "default": {
                "BACKEND": backend,
                "LOCATION": location,
                "TIMEOUT": timeout
                }
            }
        caches["default"].update(kwargs)
        settings.configure(CACHES=caches)
        import django.core.cache
        obj = django.core.cache.get_cache('default')
        return obj
