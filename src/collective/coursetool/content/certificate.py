from collective.coursetool.interfaces import ICertificate
from plone.dexterity.content import Container
from plone.namedfile import field as namedfile
from plone.supermodel import model
from zope import schema
from zope.interface import implementer


class ICertificateSchema(model.Schema):
    """schema"""


@implementer(ICertificate)
class Certificate(Container):
    """object"""
