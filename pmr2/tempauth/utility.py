from random import getrandbits
from time import time

from persistent import Persistent
from BTrees.OOBTree import OOBTree
from zope.annotation import factory
from zope.container.contained import Contained
from zope.interface import implementer
import zope.schema

from pmr2.tempauth.interfaces import ITemporaryAuth


@implementer(ITemporaryAuth)
class TemporaryAuth(Persistent, Contained):

    ttl = zope.schema.fieldproperty.FieldProperty(ITemporaryAuth['ttl'])

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

        if target[:1] == '/':
            target = request.get('SERVER_URL') + target

        if not request.get('ACTUAL_URL').startswith(target):
            return None

        return userid

TemporaryAuthFactory = factory(TemporaryAuth)
