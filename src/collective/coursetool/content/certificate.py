from collective.coursetool import _
from collective.coursetool.config import BASE_FOLDER_ID
from collective.coursetool.interfaces import ICertificate
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.interface import implementer


class ICertificateSchema(model.Schema):
    title = schema.TextLine(
        title=_("Certificate"),
        required=True,
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
        label=_("Certificate Members"),
        fields=[
            "members",
        ],
    )


@implementer(ICertificate)
class Certificate(Container):
    def members_uuids(self):
        return [m.to_object.UID() for m in self.members]
