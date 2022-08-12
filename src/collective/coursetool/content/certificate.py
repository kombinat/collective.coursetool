from collective.coursetool import _
from collective.coursetool.interfaces import ICertificate
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implementer


class ICertificateSchema(model.Schema):

    title = schema.TextLine(
        title=_("Certificate"),
        required=True,
    )


@implementer(ICertificate)
class Certificate(Container):
    """object"""
