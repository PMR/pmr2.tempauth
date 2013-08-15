import zope.interface

from Testing import ZopeTestCase as ztc
from plone.session.tests.sessioncase import FunctionalPloneSessionTestCase
from Zope2.App import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup
from Products.PloneTestCase.layer import onteardown

from pmr2.tempauth.plugin import TemporaryAuthPlugin


@onsetup
def setup():
    import pmr2.tempauth
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', pmr2.tempauth)
    zcml.load_config('tests.zcml', pmr2.tempauth.tests)
    fiveconfigure.debug_mode = False
    ztc.installPackage('pmr2.tempauth')

@onteardown
def teardown():
    pass

setup()
teardown()
ptc.setupPloneSite(products=('pmr2.tempauth',))


class FunctionalTemporaryAuthTestCase(FunctionalPloneSessionTestCase):

    def afterSetUp(self):
        FunctionalPloneSessionTestCase.afterSetUp(self)
        self.app.folder = self.folder

        if self.folder.pas.hasObject("tempauth"):
            self.app.folder.pas._delObject("tempauth")

        self.app.folder.pas._setObject("tempauth",
            TemporaryAuthPlugin("tempauth"))
