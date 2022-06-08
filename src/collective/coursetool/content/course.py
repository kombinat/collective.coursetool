from collective.coursetool import _
from collective.coursetool.interfaces import ICourse
from collective.z3cform.datagridfield.datagridfield import DataGridFieldWidgetFactory
from collective.z3cform.datagridfield.row import DictRow
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


class ICourseSchema(model.Schema):

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


@implementer(ICourse)
class Course(Container):
    """object"""
