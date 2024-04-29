from collective.coursetool import _
from collective.coursetool.browser.widgets import CourseOccurrencesFieldWidget
from collective.coursetool.config import BASE_FOLDER_ID
from collective.coursetool.interfaces import ICourse
from collective.z3cform.datagridfield.row import DictRow
from plone import api
from plone.app.vocabularies.catalog import CatalogSource
from plone.app.z3cform.widget import DateFieldWidget
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from z3c.form.browser.radio import RadioFieldWidget
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.interface import implementer

import dateparser


class ICourseOccurrences(model.Schema):
    start_date = schema.Date(
        title=_("Startdate"),
        required=False,
    )
    directives.widget(
        "start_date",
        DateFieldWidget,
        _formater_length="long",
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
    title = schema.TextLine(
        title=_("Course Title"),
        required=True,
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
        CourseOccurrencesFieldWidget,
        allow_reorder=True,
        auto_append=False,
        input_table_css_class="table table-sm",
        display_table_css_class="table table-sm",
    )

    # TODO: radio button
    type = schema.Choice(
        title=_("label_course_type", default="Type"),
        vocabulary="coursetool.vocabulary.coursetypes",
        required=True,
    )
    directives.widget("type", RadioFieldWidget)

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

    locations = RelationList(
        title=_("Course Locations"),
        default=[],
        value_type=RelationChoice(
            title=_("Location"),
            vocabulary="plone.app.vocabularies.Catalog",
        ),
        required=True,
    )
    directives.widget(
        "locations",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "basePath": f"/Plone/{BASE_FOLDER_ID}/locations",
            "selectableTypes": "coursetool.location",
            "mode": "search",
            "favorites": [],
            "browseable": False,
        },
    )

    instructors = RelationList(
        title=_("Instructors"),
        default=[],
        value_type=RelationChoice(
            title=_("Instructor"),
            source=CatalogSource(
                portal_type="coursetool.member",
                instructor=True,
            ),
        ),
        required=False,
    )
    directives.widget(
        "instructors",
        RelatedItemsFieldWidget,
        pattern_options={
            "basePath": f"/Plone/{BASE_FOLDER_ID}/members",
            "selectableTypes": "coursetool.member",
            "mode": "search",
            "favorites": [],
            "browseable": False,
        },
    )

    exams = RelationList(
        title=_("Exams"),
        value_type=RelationChoice(
            title=_("Exam"),
            vocabulary="plone.app.vocabularies.Catalog",
        ),
        required=False,
    )
    directives.widget(
        "exams",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "basePath": f"/Plone/{BASE_FOLDER_ID}/exams",
            "selectableTypes": "coursetool.exam",
            "mode": "search",
            "favorites": [],
        },
    )

    members = RelationList(
        title=_("Course Members"),
        default=[],
        value_type=RelationChoice(
            title=_("Member"),
            vocabulary="plone.app.vocabularies.Catalog",
        ),
        required=False,
    )
    directives.widget(
        "members",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "basePath": f"/Plone/{BASE_FOLDER_ID}/members",
            "selectableTypes": "coursetool.member",
            "mode": "search",
            "favorites": [],
        },
    )

    model.fieldset(
        "members",
        label=_("Course Members"),
        fields=[
            "members",
        ],
    )


# # extra magic to move fields from other behaviors
# buyable_settings = model.Fieldset(
#     'default',
#     fields=['item_net'],
# )
# buyable_fieldsets = IBuyableBehavior.getTaggedValue(FIELDSETS_KEY)
# buyable_fieldsets.append(buyable_settings)

# stock_settings = model.Fieldset(
#     'default',
#     fields=["item_available"],
# )
# stock_fieldsets = IStockBehavior.getTaggedValue(FIELDSETS_KEY)
# stock_fieldsets.append(stock_settings)


@implementer(ICourse)
class Course(Container):
    """object"""

    def get_exams(self):
        return [
            r.to_object for r in api.relation.get(source=self, relationship="exams")
        ]

    def get_instructors(self):
        return [
            r.to_object
            for r in api.relation.get(source=self, relationship="instructors")
        ]

    def get_locations(self):
        return [
            r.to_object for r in api.relation.get(source=self, relationship="locations")
        ]

    # indexer helpers for start/end date

    def start(self):
        occ = self.occurrences
        if not occ:
            return
        return dateparser.parse(f"{occ[0]['start_date']}T{occ[0]['start_time']}")

    def end(self):
        occ = self.occurrences
        if not occ:
            return
        return dateparser.parse(f"{occ[-1]['start_date']}T{occ[-1]['end_time']}")

    @property
    def location(self):
        return " - ".join([f"{l.title}, {l.city}" for l in self.get_locations()])

    def members_uuids(self):
        return [m.UID() for m in self.members]
