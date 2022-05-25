from collective.coursetool.interfaces import IExam
from plone.dexterity.content import Container
from plone.namedfile import field as namedfile
from plone.supermodel import model
from zope import schema
from zope.interface import implementer


class IExamSchema(model.Schema):
    """schema"""


@implementer(IExam)
class Exam(Container):
    """object"""
