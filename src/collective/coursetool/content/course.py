from collective.coursetool import _
from collective.coursetool.config import BASE_FOLDER_ID
from collective.coursetool.interfaces import ICourse
from collective.z3cform.datagridfield.datagridfield import DataGridFieldWidgetFactory
from collective.z3cform.datagridfield.row import DictRow
from plone.app.uuid.utils import uuidToCatalogBrain
from plone.app.vocabularies.catalog import StaticCatalogVocabulary
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.interfaces import HIDDEN_MODE
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.interface import implementer
from zope.interface import Interface


class ICourseOccurrences(model.Schema):
    start_date = schema.Date(
        title=_("Startdate"),
        required=False,
    )
    start_time = schema.Time(
        title=_("Starttime"),
        required=False,
    )
    end_time = schema.Time(
        title=_("Endtime"),
        required=False,
    )


class ICourseSchema(model.Schema):

    id = schema.ASCIILine(
        title=_("Course ID"),
        required=True,
    )

    title = schema.TextLine(
        title=_("Course Title"),
        required=True,
    )

    lessons = schema.Int(
        title=_("Course lessons"),
        description=_("Amount of course lessons (each 45 minutes)")
    )
    amount = schema.Int(
        title=_("Course units"),
    )
    time = schema.TextLine(
        title=_("Times"),
    )

    occurrences = schema.List(
        title=_("Occurrences"),
        value_type=DictRow(
            title=_("Occurrences"),
            schema=ICourseOccurrences,
        ),
        required=False,
    )
    directives.widget(
        "occurrences",
        DataGridFieldWidgetFactory,
        auto_append=False,
        input_table_css_class="table table-sm",
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


    max_members = schema.Int(
        title=_("Maximum member count"),
        required=False,
    )

    mandatory_attendance = schema.Bool(
        title=_("Mandatory attendance"),
        required=False,
    )

    practical_experience = schema.Bool(
        title=_("Practical experience"),
        required=False,
    )

    instructors = RelationList(
        title=_("Instructors"),
        default=[],
        value_type=RelationChoice(
            title=_("Instructor"),
            vocabulary='plone.app.vocabularies.Catalog'
        ),
        required=False,
    )
    directives.widget(
        "instructors",
        RelatedItemsFieldWidget,
        vocabulary='plone.app.vocabularies.Catalog',
        pattern_options={
            "basePath": f"/Plone/{BASE_FOLDER_ID}/members",
            "selectableTypes": "coursetool.member",
            "mode": "auto",
            "favorites": [],
        },
    )

    members = RelationList(
        title=_("Course Members"),
        default=[],
        value_type=RelationChoice(
            title=_("Member"),
            vocabulary='plone.app.vocabularies.Catalog'
        ),
        required=False,
    )
    directives.widget(
        "members",
        RelatedItemsFieldWidget,
        vocabulary='plone.app.vocabularies.Catalog',
        pattern_options={
            "basePath": f"/Plone/{BASE_FOLDER_ID}/members",
            "selectableTypes": "coursetool.member",
            "mode": "auto",
            "favorites": [],
        },
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

    model.fieldset(
        "members",
        label=_("Course Members"),
        fields=["members", ],
    )


@implementer(ICourse)
class Course(Container):
    """object"""

    def get_exams_titles(self):
        return [
            uuidToCatalogBrain(exam).Title
            for exam in ICourseSchema(self).exams
        ]

    def get_instructors_titles(self):
        return [
            m.to_object.Title()
            for m in ICourseSchema(self).instructors
        ]
