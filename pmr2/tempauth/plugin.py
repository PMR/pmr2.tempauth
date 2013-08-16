from zope.interface import implementer
from zope.component import getAdapter
from zope.component.hooks import getSite

from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.interfaces.plugins \
    import IAuthenticationPlugin, IExtractionPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin

from .interfaces import ITemporaryAuth, ITemporaryAuthPlugin


manage_addTemporaryAuthPlugin = PageTemplateFile(
    "../www/pmr2_tempauthAdd", globals(),
    __name__="manage_addTemporaryAuthPlugin")

def addTemporaryAuthPlugin(self, id, title='', REQUEST=None):
    """Add an TemporaryAuth plugin to a Pluggable Authentication Service.
    """
    p = TemporaryAuthPlugin(id, title)
    self._setObject(p.getId(), p)

    if REQUEST is not None:
        REQUEST["RESPONSE"].redirect("%s/manage_workspace"
                "?manage_tabs_message=TemporaryAuth+plugin+added." %
                self.absolute_url())


@implementer(ITemporaryAuthPlugin, IExtractionPlugin, IAuthenticationPlugin)
class TemporaryAuthPlugin(BasePlugin):
    """
    Temporary authentication plugin.
    """

    meta_type = "PMR Temporary Auth plugin"
    security = ClassSecurityInfo()

    def __init__(self, id, title=None):
        self._setId(id)
        self.title = title

    security.declarePrivate('extractCredentials')
    def extractCredentials(self, request):
        """
        Simplar to the extractCredentials from HTTPBasicAuthHelper, with
        the full url added rather than just the address.
        """

        creds = {}
        login_pw = request._authUserPW()

        if login_pw is None:
            # We can potentially offer a way to just authenticate by the
            # token since it's already unique to the user, but for now
            # just quit.
            return creds

        name, password = login_pw
        creds['login'] = name
        creds['password'] = password
        creds['SERVER_URL'] = request.get('SERVER_URL')
        creds['ACTUAL_URL'] = request.get('ACTUAL_URL')
        creds['_temp_auth'] = True
        return creds

    security.declarePrivate('authenticateCredentials')
    def authenticateCredentials(self, credentials):
        """
        Authenticate the collected credentials.

        For now we just rely on the ones extracted by standard basic
        http auth.
        """

        login = credentials.get('login')
        password = credentials.get('password')

        # call the utility here
        site = getSite()
        u = getAdapter(site, ITemporaryAuth)
        userid = u.validateByCredentials(password, credentials)

        if not userid == login:
            # wrong user, omit.
            return None

        pas = self._getPAS()
        info = pas._verifyUser(pas.plugins, user_id=userid)
        if info is None:
            return None  # should we raise Forbidden instead?

        return (info['id'], info['login'])
