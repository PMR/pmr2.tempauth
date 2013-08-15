import time
import unittest

import zope.component

from pmr2.tempauth.interfaces import ITemporaryAuth
from pmr2.tempauth.utility import TemporaryAuth


class TestUtility(unittest.TestCase):

    def setUp(self):
        self.utility = TemporaryAuth()

        self.mock_normal_request = {
            'SERVER_URL': 'http://nohost',
            'ACTUAL_URL': 'http://nohost/site/path/obj/@@view',
        }

        self.mock_localhost_request = {
            'SERVER_URL': 'http://localhost:8280',
            'ACTUAL_URL': 'http://localhost:8280/site/path/obj/@@view',
        }

        self.mock_vhost_request = {
            'SERVER_URL': 'http://vhost.example.com',
            'ACTUAL_URL': 'http://vhost.example.com/path/obj/@@view',
        }

    def tearDown(self):
        pass

    def test_core(self):
        ITemporaryAuth.providedBy(self.utility)
        self.assertEqual(self.utility.ttl, 90)

    def test_generate_validate(self):
        user = 'test_user_1_'
        key = self.utility.generateAccessFor(user, '/site/path/obj/@@view')

        result = self.utility.validateAccess(key, self.mock_normal_request)
        self.assertEqual(user, result)

    def test_generate_validate_expired(self):
        user = 'test_user_1_'
        key = self.utility.generateAccessFor(user, '/site/path/obj/@@view')
        self.utility.ttl = 0

        result = self.utility.validateAccess(key, self.mock_normal_request)
        self.assertNotEqual(user, result)

    def test_generate_validate_subpath(self):
        user = 'test_user_1_'
        key = self.utility.generateAccessFor(user, '/site/path/obj/')

        result = self.utility.validateAccess(key, self.mock_normal_request)
        self.assertEqual(user, result)

    def test_generate_validate_absolute_path(self):
        user = 'test_user_1_'
        key = self.utility.generateAccessFor(user,
            'http://vhost.example.com/path/obj/')

        result = self.utility.validateAccess(key, self.mock_vhost_request)
        self.assertEqual(user, result)

    def test_generate_validate_absolute_path_mismatch(self):
        user = 'test_user_1_'
        key = self.utility.generateAccessFor(user,
            'http://vhost.example.com/path/obj/')

        result = self.utility.validateAccess(key, self.mock_normal_request)
        self.assertNotEqual(user, result)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUtility))
    return suite
