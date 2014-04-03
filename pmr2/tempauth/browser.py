import json

import zope.component
from zope.component.hooks import getSite
import zope.interface
from zope.publisher.browser import BrowserPage

from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName

from pmr2.tempauth.interfaces import ITemporaryAuth


class ContextTempAuthRequestForm(BrowserPage):

    content_type = 'application/json'

    def update(self):
        # Only accept POST because this is meant for service consumption
        if self.request.method != 'POST':
            raise Unauthorized('POST only')

        # As part of meeting the web service requirements, content-type
        # restrictions will be in place.

        if self.request.getHeader('Content-type') != self.content_type:
            raise Unauthorized('invalid content type')

        mt = getToolByName(self.context, 'portal_membership')
        authutil = zope.component.getAdapter(getSite(), ITemporaryAuth)

        target = self.context.absolute_url()
        user = mt.getAuthenticatedMember().id
        key = authutil.generateAccessFor(user, target)

        self.access = {
            'user': user,
            'key': key,
            'target': target,
        }

    def render(self):
        self.request.response.setHeader('Content-type', self.content_type)
        return json.dumps(self.access)

    def __call__(self):
        self.update()
        return self.render()
