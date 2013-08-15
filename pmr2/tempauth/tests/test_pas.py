from unittest import TestSuite, makeSuite
import zope.component
from zope.interface import Interface
from zope.publisher.browser import TestRequest

from Products.PloneTestCase import PloneTestCase as ptc

from pmr2.tempauth.interfaces import ITemporaryAuth
from pmr2.tempauth.interfaces import ITemporaryAuthPlugin
from pmr2.tempauth.utility import TemporaryAuth

from .base import FunctionalTemporaryAuthTestCase


def mock_factory(cls):
    instance = cls()
    def getInstance(context):
        return instance
    return getInstance


class TestPlugin(FunctionalTemporaryAuthTestCase):

    def afterSetUp(self):
        super(TestPlugin, self).afterSetUp()
        u = mock_factory(TemporaryAuth)
        zope.component.provideAdapter(u, (Interface,), ITemporaryAuth)

    def test_interfaces(self):
        tempauth = self.folder.pas.tempauth
        self.assertTrue(ITemporaryAuthPlugin.providedBy(tempauth))

    def test_adapter(self):
        authutil = zope.component.getAdapter(object(), ITemporaryAuth)
        self.assertTrue(ITemporaryAuth.providedBy(authutil))


class TestFunctional(ptc.FunctionalTestCase):

    def test_authenticate(self):
        tempauth = self.portal.acl_users.tempauth
        authutil = zope.component.getAdapter(self.portal, ITemporaryAuth)
        request = TestRequest()

        key = authutil.generateAccessFor('test_user_1_', 'http://nohost/')
        creds = {
            'login': 'test_user_1_',
            'password': key,
            'ACTUAL_URL': 'http://nohost/view',
        }

        result = tempauth.authenticateCredentials(creds)
        self.assertEqual(('test_user_1_', 'test_user_1_'), result)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestPlugin))
    suite.addTest(makeSuite(TestFunctional))
    return suite
