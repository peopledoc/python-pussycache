from collections import OrderedDict
from unittest import TestCase

from pussycache.proxy import BaseProxy
from pussycache.cache import BaseCacheBackend


class Example(object):

    def __init__(self):
        self.users = ["Adam", "Bob", "Peter"]

    def get_users(self):
        return self.users

    def delete_user(self, user):
        self.users = [usr for usr in self.users if usr is not user]
        return self.users

    def get_user_with_kwargs(self, user=None):

        if user in ["Adam", "Bob", "Peter"]:
            return user
        else:
            raise

    def get_some_users_with_matricules(self, **users):
        """Return users and their attribute only if defined in self.user."""
        return {key: value for key, value in users.items()
                if key in self.users}


class TestProxy(TestCase):

    def setUp(self):
        self.proxied_object = Example()
        self.proxy = BaseProxy(
            self.proxied_object,
            cache=BaseCacheBackend(300),
            invalidate_methods={
                "delete_user": ["get_users",
                                "get_user_with_kwargs",
                                "get_some_users_with_matricules"
                                ]},
            cached_methods=["get_users",
                            "get_user_with_kwargs",
                            "get_some_users_with_matricules"]
        )

    def test_in_the_cache(self):

        users = self.proxy.get_users()
        self.assertEqual(users, self.proxy._cache.get("get_users()[]"))
        self.proxy.get_user_with_kwargs(user="Bob")
        self.assertEqual(
            "Bob",
            self.proxy._cache.get("get_user_with_kwargs()[('user', 'Bob')]"))
        self.assertEqual(["Adam", "Peter"], self.proxy.delete_user("Bob"))
        self.assertEqual(
            None,
            self.proxy._cache.get("get_user_with_kwargs()[('user', 'Bob')]"))

    def test_sorted_kwargs(self):
        # First call
        users = OrderedDict([('Adam', 123),
                             ('Yohann', 456),
                             ('Bob', 789)])
        first_call = self.proxy.get_some_users_with_matricules(**users)

        self.assertDictEqual(first_call, {'Adam': 123, 'Bob': 789})

        count = len(self.proxy._cache.store.keys())

        # Second Call
        users2 = OrderedDict([('Yohann', 456),
                              ('Adam', 123),
                             ('Bob', 789)])
        second_call = self.proxy.get_some_users_with_matricules(**users2)

        self.assertDictEqual(second_call, {'Adam': 123, 'Bob': 789})

        # Check that second call does not create another key
        self.assertEqual(len(self.proxy._cache.store.keys()), count)
