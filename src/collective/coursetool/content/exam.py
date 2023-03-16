from collective.coursetool import _
from collective.coursetool.config import BASE_FOLDER_ID
from collective.coursetool.interfaces import IExam
from collective.z3cform.datagridfield.datagridfield import DataGridFieldWidgetFactory
from collective.z3cform.datagridfield.row import DictRow
from plone import api
from plone.app.z3cform.widget import DatetimeFieldWidget
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.app.z3cform.widget import SelectFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.interface import implementer


class IMembers(model.Schema):

    member = RelationChoice(
        title=_("Member"),
        vocabulary="plone.app.vocabularies.Catalog",
        required=False,
    )
    directives.widget(
        "member",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "basePath": f"/Plone/{BASE_FOLDER_ID}/members",
            "selectableTypes": "coursetool.member",
            "mode": "search",
            "favorites": [],
            "browseable": False,
        },
    )

    success = schema.Bool(
        title=_("Exam successfully passed"),
        required=False,
        default=False,
    )


class IExamSchema(model.Schema):

    title = schema.TextLine(
        title=_("Exam"),
        required=True,
    )

    date = schema.Datetime(
        title=_("Exam date"),
    )
    directives.widget(
        "date",
        DatetimeFieldWidget,
        _formater_length="full",
    )

    location = RelationList(
        title=_("Course Location"),
        default=[],
        value_type=RelationChoice(
            title=_("Location"),
            vocabulary="plone.app.vocabularies.Catalog",
        ),
        required=True,
    )
    directives.widget(
        "location",
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

    types = schema.Tuple(
        title=_("Types"),
        value_type=schema.Choice(
            vocabulary="coursetool.vocabulary.examtypes",
        ),
        required=False,
    )
    directives.widget(
        "types",
        SelectFieldWidget,
        pattern_options={
            "allowNewItems": "false",
        },
    )

    members = schema.List(
        title=_("Course Members"),
        value_type=DictRow(
            title="Member",
            schema=IMembers,
        ),
        required=False,
    )
    directives.widget(
        "members",
        DataGridFieldWidgetFactory,
        input_table_css_class="table table-sm",
        display_table_css_class="table table-sm",
    )

    model.fieldset(
        "members",
        label=_("Exam Members"),
        fields=[
            "members",
        ],
    )


@implementer(IExam)
class Exam(Container):
    """object"""

    def start(self):
        return self.date

    def get_locations(self):
        return [
            r.to_object
            for r in api.relation.get(source=self, relationship="location")
        ]

    def members_uuids(self):
        _uids = []
        for m in self.members:
            if isinstance(m["member"], str):
                _uids.append(m["member"])
            else:
                _uids.append(m["member"].UID())
