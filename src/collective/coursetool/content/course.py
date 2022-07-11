from collective.coursetool import _
from collective.coursetool.interfaces import ICourse
from collective.z3cform.datagridfield.datagridfield import DataGridFieldWidgetFactory
from collective.z3cform.datagridfield.row import DictRow
from plone.app.uuid.utils import uuidToCatalogBrain, uuidToObject
from plone.app.vocabularies.catalog import StaticCatalogVocabulary
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.app.z3cform.widget import SelectFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.interfaces import HIDDEN_MODE
from zope import schema
from zope.interface import implementer
from zope.interface import Interface


class IMemberId(model.Schema):

    member_id = schema.Choice(
        title=_("Member"),
        required=True,
        vocabulary=StaticCatalogVocabulary(
            {
                "portal_type": "coursetool.member",
                "sort_on": "sortable_title",
            },
            title_template="{brain.Title}",
        ),
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
        required=True,
    )

    title = schema.TextLine(
        title=_("Course"),
        required=True,
    )

    start = schema.Datetime(
        title=_("label_course_start", default="Start"),
        required=True,
    )

    end = schema.Datetime(
        title=_("label_course_end", default="End"),
        required=True,
    )

    location = schema.TextLine(
        title=_("label_course_location", default="Location"),
    )

    type = schema.Tuple(
        title=_("label_course_type", default="Type"),
        value_type=schema.Choice(
            vocabulary="coursetool.vocabulary.coursetypes",
        ),
        required=True,
    )
    directives.widget("type", CheckBoxFieldWidget)

    duration = schema.Int(
        title=_("Duration"),
        description=_("Course duration in hours"),
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
        title=_("Exams"),
        value_type=schema.Choice(
            vocabulary=StaticCatalogVocabulary(
                {
                    "portal_type": "coursetool.exam",
                    "sort_on": "sortable_title",
                },
                title_template="{brain.Title}",
            ),
        ),
    )


@implementer(ICourse)
class Course(Container):
    """object"""

    def get_exams(self):
        return ICourseSchema(self).exams

    def get_exams_titles(self):
        return [
            uuidToCatalogBrain(exam).Title
            for exam in self.get_exams()
        ]
