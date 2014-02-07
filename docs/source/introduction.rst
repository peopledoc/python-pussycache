Python pussy cache
==================

Python pussy cache is a Cache system for python objects.

Cache backends can be in-memory or redis/ You can even use the django
cache framework with Python-pussy-cache.

Given a one of the cache backends and any Python class you have define,
Python-pussy-cache will cache the results of methods you have define and
will also manage the cache invalidation by timestamp or with methods you
have defined.

|Build Status|

Here is an example to make the thing clearer

.. code:: python

    import time
    from pussycache.proxy import BaseProxy
    from pussycache.cache import BaseCacheBackend
    # Here is a simple class where some methods need to be cached

    class MyClass(object):

          def a_long_task(self, delta):
              time.sleep(delta)
              return delta

          def forget_about_time(self):
              return None

    # We set an in memory cache backend with a TTL of 30 seconds.

    cache = BaseCacheBackend(30)

    cache_proxy = BaseProxy(MyClass(), cache=cache,
                 cached_methods=["a_long_task"],
                 invalidate_methods={"forget_about_time": ["a_long_task"]})

    cachedinstance = cache_proxy
    # your cachedinstance is now
    # ready to use. It will just work like a regular MyClass object

    print cachedinstance.a_long_task(10)
    # 10 seconds later
    10
    # if we call the same method a second time:
    print cachedinstance.a_long_task(10)
    10
    # result is returned immediatly because it's in the cache
    # but
    print cachedinstance.a_long_task(3)
    3
    # with different parameters, the result is not cached yet.
    # if you want to invalidate the cache for this method:
    print cachedinstance.forget_about_time()
    print cachedinstance.a_long_task(10)
    # 10 seconds later
    10

Of course, If you need direct access to the cache backend, you can call
it directly. Let's say you need to invalidate ALL the cache :

.. code:: python


    cachedinstance._cache.clear()

The same apply if you need to call directly the cache:

.. code:: python

    cachedinstance._cache.set("mykey", "my value", 10)
    cachedinstance._cache.get("mykey")
    "my value"
    #and 10 seconds later:
    cachedinstance._cache.get("mykey")
    #the value is gone from the cache

Tests
-----

To run test, just install tox with ``pip install tox`` and run

::

    tox

.. |Build Status| image:: https://travis-ci.org/novapost/python-pussycache.png?branch=master
   :target: https://travis-ci.org/novapost/python-pussycache
