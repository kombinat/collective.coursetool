from collective.coursetool import _
from collective.coursetool.config import BASE_FOLDER_ID
from collective.coursetool.interfaces import IExam
from plone import api
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.interface import implementer


class IExamSchema(model.Schema):

    title = schema.TextLine(
        title=_("Exam"),
        required=True,
    )

    date = schema.Datetime(
        title=_("Exam date"),
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

    members = RelationList(
        title=_("Course Members"),
        default=[],
        value_type=RelationChoice(
            title=_("Member"), vocabulary="plone.app.vocabularies.Catalog"
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
        label=_("Exam Members"),
        fields=[
            "members",
        ],
    )


@implementer(IExam)
class Exam(Container):
    """object"""

    def get_locations(self):
        return [
            r.to_object
            for r in api.relation.get(source=self, relationship="location")
        ]
