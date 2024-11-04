from collective.coursetool import _
from collective.coursetool.interfaces import ILocation
from plone.app.dexterity.textindexer.directives import searchable
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implementer


class ILocationSchema(model.Schema):
    searchable("title")
    title = schema.TextLine(title=_("Location Title"))


@implementer(ILocation)
class Location(Container):
    """object"""
