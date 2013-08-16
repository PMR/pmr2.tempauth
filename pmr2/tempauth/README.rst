Word of Caution
===============

As there may be unknown security risks involved with this experimental
module, it's up to the implementation of services that require such a
feature to provide their own zcml declaration on their subclasses for
invoking the temporary password generation.

Demonstration
=============

For testing purposes, a view is already registered by the testing zcml.
To complete the test, add some content first::

    >>> from Products.PloneTestCase.setup import default_user, default_password
    >>> self.login(default_user)
    >>> self.setRoles(['Manager'])
    >>> o = self.portal.news.invokeFactory('News Item', id='test')
    >>> self.portal.news.test.edit(text='Please ignore.', title='Test News')
    >>> o = self.portal.news.invokeFactory('News Item', id='reset')
    >>> self.portal.news.reset.edit(text='All the things.', title='Reset')

Naturally private content results in a login page::

    >>> from Testing.testbrowser import Browser
    >>> main_browser = Browser()
    >>> portal_url = self.portal.absolute_url()
    >>> main_browser.open(portal_url + '/news/test')
    >>> 'Please ignore' in main_browser.contents
    False

Normal logins will naturally work::

    >>> main_browser.open(portal_url + '/news/test')
    >>> main_browser.getControl(name='__ac_name').value = default_user
    >>> main_browser.getControl(name='__ac_password').value = default_password
    >>> main_browser.getControl(name='submit').click()
    >>> 'Please ignore' in main_browser.contents
    True

Here's the fun part: make the temporary password.  Try getting that::

    >>> target = portal_url + '/request_temporary_password'
    >>> main_browser.open(target)
    >>> 'Insufficient Privileges' in main_browser.contents
    True

Yeah it doesn't like that by default, we need to make a POST::

    >>> main_browser.addHeader('Content-type', 'application/json')
    >>> main_browser.open(target, data='{}')
    >>> 'Insufficient Privileges' in main_browser.contents
    True

Or not.  Since the standard test browser class can't avoid using the
wrong content type (the override didn't work here), we do this::

    >>> import json
    >>> from zope.publisher.browser import TestRequest
    >>> from pmr2.tempauth.browser import ContextTempAuthRequestForm
    >>> req = TestRequest(HTTP_CONTENT_TYPE='application/json')
    >>> req.method = 'POST'
    >>> view = ContextTempAuthRequestForm(self.portal, req)
    >>> creds = json.loads(view())
    >>> creds['user'] == default_user
    True

Cool, got a temporary password.  See if we can log in::

    >>> from Testing.testbrowser import Browser
    >>> alt = Browser()
    >>> portal_url = self.portal.absolute_url()
    >>> alt.open(portal_url + '/news/test')
    >>> alt.getControl(name='__ac_name').value = creds['user']
    >>> alt.getControl(name='__ac_password').value = creds['key']
    >>> alt.getControl(name='submit').click()
    >>> 'Please ignore' in alt.contents
    False

And the answer must be **NO**.  The idea for this add-on is to grant
http protocol level auth for clients that only speaks http.  So the only
way to use this is this::

    >>> auth = '%(user)s:%(key)s' % creds
    >>> alt.addHeader('Authorization', 'Basic %s' % auth.encode('base64'))
    >>> alt.open(portal_url + '/news/test')
    >>> 'Please ignore' in alt.contents
    True
    >>> alt.open(portal_url + '/news/reset')
    >>> 'All the things' in alt.contents
    True

Naturally, if we replace the timeout with 0, this would effectively
disable this add-on::

    >>> import zope.component
    >>> from pmr2.tempauth.interfaces import ITemporaryAuth
    >>> authutil = zope.component.getAdapter(self.portal, ITemporaryAuth)
    >>> authutil.ttl = 0
    >>> auth = '%(user)s:%(key)s' % creds
    >>> alt.addHeader('Authorization', 'Basic %s' % auth.encode('base64'))
    >>> alt.open(portal_url + '/news/test')
    >>> 'Please ignore' in alt.contents
    False
    >>> authutil.ttl = 60

Another feature that needs testing is the scope limitation.  If the
service integrators were to restrict their view declaration to specific
object types, it can serve as a safeguard against overly broad access
(i.e. restrict access to the object that clients require protocol level
access).  Here if we request the token at one specific object::

    >>> view = ContextTempAuthRequestForm(self.portal.news.test, req)
    >>> creds = json.loads(view())
    >>> auth = '%(user)s:%(key)s' % creds
    >>> alt = Browser()
    >>> alt.addHeader('Authorization', 'Basic %s' % auth.encode('base64'))
    >>> alt.open(portal_url + '/news/test')
    >>> 'Please ignore' in alt.contents
    True

It remains usable for the context it was requested for, and if we try the
other news item, it will be prohibited::

    >>> alt.open(portal_url + '/news/reset')
    >>> 'All the things' in alt.contents
    False

Naturally it is up to the integrators to fine-tune how access is granted
with the usage of this default view, or their customized views.
