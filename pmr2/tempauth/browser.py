import json

import zope.component
from zope.component.hooks import getSite
import zope.interface
from zope.publisher.browser import BrowserPage

from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName

from pmr2.tempauth.interfaces import ITemporaryAuth


class ContextTempAuthRequestForm(BrowserPage):

    accept_content_type = 'application/json'

    def update(self):
        # Only accept POST because this is meant for service consumption
        if self.request.method != 'POST':
            raise Unauthorized('POST only')

        # As part of meeting the web service requirements, content-type
        # restrictions will be in place.

        if self.request.getHeader('Content-type') != self.accept_content_type:
            raise Unauthorized('invalid content type')

        mt = getToolByName(self.context, 'portal_membership')
        self.target = self.context.absolute_url()
        self.user = mt.getAuthenticatedMember().id

    def render(self):
        authutil = zope.component.getAdapter(getSite(), ITemporaryAuth)
        key = authutil.generateAccessFor(self.user, self.target)

        self.request.response.setHeader('Content-type', 'application/json')
        return json.dumps({
            'user': self.user,
            'key': key,
            'target': self.target,
        })

    def __call__(self):
        self.update()
        return self.render()
