from collective.coursetool.interfaces import ICourse
from plone.dexterity.content import Container
from plone.namedfile import field as namedfile
from plone.supermodel import model
from zope import schema
from zope.interface import implementer


class ICourseSchema(model.Schema):
    """schema"""


@implementer(ICourse)
class Course(Container):
    """object"""
