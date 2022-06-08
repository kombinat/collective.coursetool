from collective.coursetool import _
from collective.coursetool.config import BASE_FOLDER_ID
from collective.coursetool.interfaces import IMember
from plone import api
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.app.z3cform.widget import SelectFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implementer


class IMemberSchema(model.Schema):
    """schema"""

    id = schema.TextLine(
        title=_("Customer Nr"),
        required=True,
    )

    salutation = schema.TextLine(
        title=_("Salutation"),
        required=False,
    )

    graduation = schema.TextLine(
        title=_("Graduation"),
        required=False,
    )

    lastname = schema.TextLine(
        title=_("Lastname"),
    )
    firstname = schema.TextLine(
        title=_("Firstname"),
    )

    address = schema.TextLine(title=_("Address"), required=False)
    address2 = schema.TextLine(title=_("Address2"), required=False)

    cty_code = schema.TextLine(title=_("Country"), required=False)

    zip_code = schema.TextLine(
        title=_("ZIP Code"),
        required=False,
    )

    city = schema.TextLine(
        title=_("City"),
        required=False,
    )

    website = schema.TextLine(
        title=_("Internet Address"),
        required=False,
    )

    booking_nr = schema.TextLine(
        title=_("Booking Nr"),
        required=False,
    )

    inactive = schema.Bool(
        title=_("Inactive"),
        required=False,
        default=False,
    )

    email = schema.TextLine(
        title=_("EMail"),
        required=False,
    )

    phone = schema.TextLine(
        title=_("Phone"),
        required=False,
    )

    mobile_phone = schema.TextLine(
        title=_("Mobile Phone"),
        required=False,
    )

    fax = schema.TextLine(
        title=_("Fax"),
        required=False,
    )

    birthday = schema.Date(
        title=_("Birthday"),
        required=False,
    )

    salutation_personal = schema.Bool(
        title=_("Personal Saluation"),
        required=False,
        default=False,
    )

    salutation_letter = schema.TextLine(
        title=_("Salutation Letter"),
        required=False,
    )

    payed = schema.Bool(
        title=_("Payed"),
        required=False,
        default=False,
    )

    state = schema.Choice(
        title=_("State"),
        vocabulary="coursetool.vocabulary.memberstates",
        required=False,
    )
    directives.widget("state", SelectFieldWidget)

    qualification = schema.Tuple(
        title=_("Qualification"),
        value_type=schema.TextLine(),
        required=False,
    )
    directives.widget(
        "qualification",
        SelectFieldWidget,
        vocabulary="coursetool.vocabulary.memberqualifications",
        pattern_options={
            "allowNewItems": "false",
        },
    )

    partner_type = schema.Tuple(
        title=_("Partnertype"),
        value_type=schema.Choice(
            vocabulary="coursetool.vocabulary.partnertypes",
        ),
        required=False,
    )
    directives.widget(
        "partner_type",
        AjaxSelectFieldWidget,
        pattern_options={
            "allowNewItems": "true",
        },
    )

    model.fieldset(
        "metadata",
        label=_("Metadata"),
        fields=[
            "salutation_letter", "payed", "state", "qualification",
            "partner_type",
        ],
    )


@implementer(IMember)
class Member(Container):
    """object"""

    @property
    def title(self):
        title_parts = [
            self.lastname,
            self.firstname,
        ]

        return " ".join([p for p in title_parts if p])

    @title.setter
    def title(self, value):
        pass

    def get_address(self):
        return [
            adr for adr in (
                self.address,
                self.zip_code,
                self.city,
            ) if adr
        ]

    @property
    def address_inline(self):
        return ", ".join(self.get_address())
