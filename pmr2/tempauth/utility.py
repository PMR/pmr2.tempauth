from random import getrandbits
from time import time

from persistent import Persistent
from BTrees.OOBTree import OOBTree
from zope.annotation import factory
from zope.container.contained import Contained
from zope.interface import implementer
from zope.component import adapter
from zope.schema.fieldproperty import FieldProperty
from zope.annotation.interfaces import IAttributeAnnotatable

from pmr2.tempauth.interfaces import ITemporaryAuth


@implementer(ITemporaryAuth)
@adapter(IAttributeAnnotatable)
class TemporaryAuth(Persistent, Contained):

    ttl = FieldProperty(ITemporaryAuth['ttl'])

    def __init__(self):
        self._keys = OOBTree()

    def generateAccessFor(self, userid, target):
        """
        Safeguards on what the target is should be done by the caller of
        this method.
        """

        key = '%040x' % getrandbits(160)
        self._keys[key] = (int(time()), userid, target)
        return key

    def validateAccess(self, key, request):
        token = self._keys.get(key, None)
        if not token:
            return None

        created_at, userid, target = token

        if created_at + self.ttl < time():
            # Expired token, by removing it also.
            self._keys.pop(key, None)
            # Others will not be removed, figure out how to prune later.
            return None

        server_url = request.get('SERVER_URL', '')
        actual_url = request.get('ACTUAL_URL', '')

        if target[:1] == '/':
            target = server_url + target

        if not (actual_url and actual_url.startswith(target)):
            return None

        return userid

    def validateByCredentials(self, key, credentials):
        """
        For the PAS plugin.
        """

        if not credentials.get('_temp_auth'):
            return None
        return self.validateAccess(key, credentials)

TemporaryAuthFactory = factory(TemporaryAuth)
