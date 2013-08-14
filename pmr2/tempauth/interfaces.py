import zope.interface
import zope.schema


class ITemporaryAuth(zope.interface.Interface):

    ttl = zope.schema.Int(
        title=u'Time To Live',
        default=90,
    )

    def generateAccessFor(user, target):
        """
        Generates a user specific temporary auth token valid for the
        specific target.

        Returns a key.
        """

    def validateAccess(key, request):
        """
        Validate the access using the the user against the request.
        """


class ITemporaryAuthPlugin(zope.interface.Interface):
    """
    The PAS plugin interface.
    """
