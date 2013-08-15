from logging import getLogger
from zope.component.hooks import getSite

from Products.CMFCore.utils import getToolByName


def createPlugin(site, id_):
    acl = getToolByName(site, "acl_users")
    acl.manage_addProduct["pmr2.tempauth"].addTemporaryAuthPlugin(
        id=id_, title='TemporaryAuth authentication plugin')


def activatePlugin(site, id_):
    logger = getLogger('pmr2.tempauth')
    acl = getToolByName(site, "acl_users")
    plugin = getattr(acl, id_)
    interfaces = plugin.listInterfaces()

    activate = []

    for info in acl.plugins.listPluginTypeInfo():
        interface = info["interface"]
        interface_name = info["id"]
        if plugin.testImplements(interface):
            activate.append(interface_name)
            logger.info("Activating interface %s for plugin %s" % 
                    (interface_name, info["title"]))

    plugin.manage_activateInterfaces(activate)


def importVarious(context):
    # Only run step if a flag file is present (e.g. not an extension profile)
    if context.readDataFile('tempauth-pas.txt') is None:
        return

    id_ = 'tempauth'
    site = context.getSite()

    acl = getToolByName(site, "acl_users")
    installed = acl.objectIds()
    if id_ not in installed:
        createPlugin(site, id_)
        activatePlugin(site, id_)
