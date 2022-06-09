from collective.coursetool import _
from collective.coursetool.interfaces import IExam
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implementer


class IExamSchema(model.Schema):

    id = schema.ASCIILine(
        title=_("Exam ID"),
        required=False,
    )

    title = schema.TextLine(
        title=_("Exam"),
        required=True,
    )


@implementer(IExam)
class Exam(Container):
    """object"""
