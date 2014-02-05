from unittest import TestCase
from pussycache.proxy import BaseProxy
from pussycache.cache import BaseCacheBackend


class Example(object):

    def __init__(self):
        self.users = []

    def get_users(self):
        self.users = ["Adam", "Bob", "Peter"]

    def delete_user(self, user):
        self.users = [usr for usr in self.users if usr is not user]

    def get_user_with_kwargs(self, user=None):
        if user in ["Adam", "Bob", "Peter"]:
            return user


class TestProxy(TestCase):

    def setUp(self):
        self.proxy = BaseProxy(
            backend=Example,
            cache=BaseCacheBackend(300),
            invalidate_methods={"delete_user": ["get_users", "delete_user"]},
            cached_methods=["get_users", "get_user_with_kwargs"]
            )
        self.backend = self.proxy.backend

    def test_in_the_cache(self):
        users = self.backend.get_users()
        self.assertEqual(users, self.backend.cache.get("get_users()"))
        self.backend.get_user_with_kwargs(user="Bob")
        self.assertEqual(
            "Bob",
            self.backend.cache.get("get_user_with_kwargs(){'user': 'Bob'}"))
        self.backend.delete_user("Bob")
        self.assertEqual(
            None,
            self.backend.cache.get("get_user_with_kwargs(){'user': 'Bob'}"))
