from unittest import TestCase
from pussycache.cache import BaseCacheBackend


class TestCacheBackend(TestCase):
    """ Base tests on backend """

    def test_add(self):
        cache = BaseCacheBackend(100)
        cache.add('add_key', 'Initial value')
        result = cache.get('add_key')
        self.assertEqual(result, 'Initial value')
