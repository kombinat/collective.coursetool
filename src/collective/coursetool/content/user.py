from collective.coursetool.interfaces import IMember
from plone.dexterity.content import Container
from plone.namedfile import field as namedfile
from plone.supermodel import model
from zope import schema
from zope.interface import implementer


class IMemberSchema(model.Schema):
    """schema"""


@implementer(IMember)
class Member(Container):
    """object"""
