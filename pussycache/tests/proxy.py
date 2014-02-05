from unittest import TestCase
from pussycache.proxy import BaseProxy
from pussycache.cache import BaseCacheBackend


class Example(object):

    def __init__(self):
        self.users = []

    def get_users(self):
        self.users = ["Adam", "Bob", "Peter"]
        return self.users

    def delete_user(self, user):
        self.users = [usr for usr in self.users if usr is not user]


class TestProxy(TestCase):

    def setUp(self):
        self.proxied_object = Example()
        self.proxy = BaseProxy(
            self.proxied_object,
            cache=BaseCacheBackend(300),
            invalidate_methods={"delete_user": ["get_users"]},
            cached_methods=["get_users"]
        )

    def test_in_the_cache(self):
        users = self.proxy.get_users()
        self.assertEqual(users, self.proxy._cache.get("get_users()"))
