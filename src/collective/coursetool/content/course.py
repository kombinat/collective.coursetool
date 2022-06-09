from collective.coursetool import _
from collective.coursetool.interfaces import ICourse
from collective.z3cform.datagridfield.datagridfield import DataGridFieldWidgetFactory
from collective.z3cform.datagridfield.row import DictRow
from plone.app.vocabularies.catalog import StaticCatalogVocabulary
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.app.z3cform.widget import SelectFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from z3c.form.interfaces import HIDDEN_MODE
from zope import schema
from zope.interface import implementer
from zope.interface import Interface


class IMemberId(model.Schema):

    member_id = schema.Choice(
        title=_("Member"),
        required=True,
        vocabulary="coursetool.vocabulary.members",
    )
    directives.widget(
        "member_id",
        AjaxSelectFieldWidget,
    )


class IExamId(model.Schema):

    exam_id = schema.Choice(
        title=_("Exam"),
        required=True,
        vocabulary=StaticCatalogVocabulary(
            {
                "portal_type": "coursetool.exam",
                "sort_on": "sortable_title",
            },
            title_template="{brain.Title}",
        ),
    )
    directives.widget(
        "exam_id",
        SelectFieldWidget,
    )


class ICourseSchema(model.Schema):

    id = schema.ASCIILine(
        title=_("Course ID"),
        required=False,
    )

    title = schema.TextLine(
        title=_("Course"),
        required=True,
    )

    instructors = schema.List(
        title=_("Instructors"),
        value_type=DictRow(title="instructor", schema=IMemberId),
        required=True,
    )
    directives.widget(
        "instructors",
        DataGridFieldWidgetFactory,
        allow_reorder=True,
    )

    members = schema.List(
        title=_("Members"),
        value_type=DictRow(title="Member", schema=IMemberId),
        required=True,
    )
    directives.widget(
        "members",
        DataGridFieldWidgetFactory,
        allow_reorder=True,
    )

    exams = schema.List(
        title=_("Exams"), value_type=DictRow(title="Exam", schema=IExamId)
    )
    directives.widget(
        "exams",
        DataGridFieldWidgetFactory,
        allow_reorder=True,
    )


@implementer(ICourse)
class Course(Container):
    """object"""
