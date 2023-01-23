from collective.coursetool import _
from collective.coursetool.config import BASE_FOLDER_ID
from collective.coursetool.interfaces import IMember
from dexterity.membrane.behavior.user import MembraneUserProperties
from plone.app.users.schema import IRegisterSchema
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.app.z3cform.widget import DateFieldWidget
from plone.app.z3cform.widget import SelectFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.namedfile import field as namedfile
from plone.supermodel import model
from z3c.form.interfaces import IEditForm
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


class IRegistration(IRegisterSchema):
    first_name = schema.TextLine(title=_("Firstname"))
    last_name = schema.TextLine(title=_("Lastname"))
    email = schema.TextLine(title=_("Email"))


class IMemberSchema(model.Schema):
    """schema"""

    id = schema.TextLine(title=_("Customer Nr"), required=True)
    salutation = schema.TextLine(title=_("Salutation"), required=False)
    first_name = schema.TextLine(title=_("Firstname"), required=False)
    last_name = schema.TextLine(title=_("Lastname"), required=False)
    graduation = schema.TextLine(title=_("Graduation"), required=False)
    address = schema.TextLine(title=_("Address"), required=False)
    address2 = schema.TextLine(title=_("Address2"), required=False)
    zip_code = schema.TextLine(title=_("ZIP Code"), required=False)
    city = schema.TextLine(title=_("City"), required=False)
    cty_code = schema.TextLine(title=_("Country"), required=False)

    email = schema.TextLine(title=_("EMail"), required=False)
    website = schema.TextLine(title=_("Internet Address"), required=False)
    booking_nr = schema.TextLine(title=_("Booking Nr"), required=False)
    inactive = schema.Bool(title=_("Inactive"), required=False, default=False)
    phone = schema.TextLine(title=_("Phone"), required=False)
    mobile_phone = schema.TextLine(title=_("Mobile Phone"), required=False)
    fax = schema.TextLine(title=_("Fax"), required=False)

    birthday = schema.Date(title=_("Birthday"), required=False)
    directives.widget(
        "birthday",
        DateFieldWidget,
        _formater_length="long",
    )

    salutation_personal = schema.Bool(
        title=_("Personal Saluation"), required=False, default=False
    )
    salutation_letter = schema.TextLine(title=_("Salutation Letter"), required=False)
    payed = schema.Bool(title=_("Payed"), required=False, default=False)
    picture = namedfile.NamedBlobImage(
        title=_("User Image"),
        required=False,
    )

    instructor = schema.Bool(
        title=_("Instructor"),
        required=False,
    )

    state = schema.Choice(
        title=_("State"),
        vocabulary="coursetool.vocabulary.memberstates",
        required=False,
    )
    directives.widget("state", SelectFieldWidget)

    qualification = schema.Tuple(
        title=_("Qualification"),
        value_type=schema.Choice(
            vocabulary="coursetool.vocabulary.memberqualifications",
        ),
        required=False,
    )
    directives.widget(
        "qualification",
        SelectFieldWidget,
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

    # field visibility
    directives.omitted("id")
    directives.no_omit(IEditForm, "id")

    # field permissions
    directives.read_permission(
        booking_nr="cmf.ManagePortal",
        inactive="cmf.ManagePortal",
        salutation_personal="cmf.ManagePortal",
        salutation_letter="cmf.ManagePortal",
        payed="cmf.ManagePortal",
        state="cmf.ManagePortal",
        qualification="cmf.ManagePortal",
        partner_type="cmf.ManagePortal",
    )
    directives.write_permission(
        id="cmf.ManagePortal",
        booking_nr="cmf.ManagePortal",
        inactive="cmf.ManagePortal",
        salutation_personal="cmf.ManagePortal",
        salutation_letter="cmf.ManagePortal",
        payed="cmf.ManagePortal",
        state="cmf.ManagePortal",
        qualification="cmf.ManagePortal",
        partner_type="cmf.ManagePortal",
    )

    model.fieldset(
        "metadata",
        label=_("Metadata"),
        fields=[
            "id",
            "booking_nr",
            "salutation_personal",
            "salutation_letter",
            "payed",
            "state",
            "inactive",
            "qualification",
            "partner_type",
        ],
    )


@implementer(IMember)
class Member(Container):
    """object"""

    @property
    def title(self):
        title_parts = [
            self.last_name or self.lastname,
            self.first_name or self.firstname,
        ]

        return " ".join([p for p in title_parts if p])

    @title.setter
    def title(self, value):
        pass

    def get_full_name(self):
        return self.title

    def get_address(self):
        return [
            adr
            for adr in (
                self.address,
                self.zip_code,
                self.city,
            )
            if adr
        ]

    @property
    def address_inline(self):
        return ", ".join(self.get_address())


@adapter(IMember)
class UserProperties(MembraneUserProperties):

    property_map = dict(
        email="email",
        first_name="first_name",
        firstname="first_name",
        last_name="last_name",
        lastname="last_name",
    )
