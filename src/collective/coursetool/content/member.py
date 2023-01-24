from collective.coursetool import _
from collective.coursetool.config import BASE_FOLDER_ID
from collective.coursetool.interfaces import IMember
from dexterity.membrane.behavior.user import MembraneUserProperties
from plone.app.dexterity import textindexer
from plone.app.users.schema import IRegisterSchema
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.app.z3cform.widget import DateFieldWidget
from plone.app.z3cform.widget import SelectFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.formwidget.namedfile import NamedImageFieldWidget
from plone.namedfile import field as namedfile
from plone.supermodel import model
from z3c.form.browser.text import TextFieldWidget
from z3c.form.interfaces import IEditForm
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


class IRegistration(IRegisterSchema):
    first_name = schema.TextLine(title=_("Firstname"))
    last_name = schema.TextLine(title=_("Lastname"))
    email = schema.TextLine(title=_("Email"))
    picture = namedfile.NamedBlobImage(
        title=_("User Image"),
        description=_("Upload your Passfoto (5MB max size)"),
    )
    passport_image = namedfile.NamedBlobImage(
        title=_("Passport Image"),
        description=_(
            "Please upload a foto of your passport "
            "to validate your identity."),
    )


class IMemberSchema(model.Schema):
    """schema"""

    salutation = schema.TextLine(title=_("Salutation"), required=False)
    graduation = schema.TextLine(title=_("Graduation"), required=False)
    first_name = schema.TextLine(title=_("Firstname"), required=False)
    last_name = schema.TextLine(title=_("Lastname"), required=False)
    address = schema.TextLine(title=_("Address"), required=False)
    address2 = schema.TextLine(title=_("Address2"), required=False)
    zip_code = schema.TextLine(title=_("ZIP Code"), required=False)
    city = schema.TextLine(title=_("City"), required=False)
    cty_code = schema.TextLine(title=_("Country"), required=False)

    email = schema.TextLine(title=_("EMail"), required=True)
    website = schema.TextLine(title=_("Internet Address"), required=False)
    phone = schema.TextLine(title=_("Phone"), required=False)
    mobile_phone = schema.TextLine(title=_("Mobile Phone"), required=False)
    fax = schema.TextLine(title=_("Fax"), required=False)

    birthday = schema.Date(title=_("Birthday"), required=False)
    directives.widget(
        "birthday",
        DateFieldWidget,
        _formater_length="long",
    )

    picture = namedfile.NamedBlobImage(
        title=_("User Image"),
    )
    passport_image = namedfile.NamedBlobImage(
        title=_("Passport Image"),
    )

    # layout wrapper CSS classes
    directives.widget("salutation", TextFieldWidget, wrapper_css_class="col-lg-1")
    directives.widget("graduation", TextFieldWidget, wrapper_css_class="col-lg-1")
    directives.widget("first_name", TextFieldWidget, wrapper_css_class="col-lg-5")
    directives.widget("last_name", TextFieldWidget, wrapper_css_class="col-lg-5")
    directives.widget("address", TextFieldWidget, wrapper_css_class="col-lg-7")
    directives.widget("address2", TextFieldWidget, wrapper_css_class="col-lg-5")
    directives.widget("zip_code", TextFieldWidget, wrapper_css_class="col-lg-2")
    directives.widget("city", TextFieldWidget, wrapper_css_class="col-lg-5")
    directives.widget("cty_code", TextFieldWidget, wrapper_css_class="col-lg-5")
    directives.widget("phone", TextFieldWidget, wrapper_css_class="col-lg-4")
    directives.widget("mobile_phone", TextFieldWidget, wrapper_css_class="col-lg-4")
    directives.widget("website", TextFieldWidget, wrapper_css_class="col-lg-4")
    directives.widget("fax", TextFieldWidget, wrapper_css_class="col-lg-6")
    directives.widget("birthday", TextFieldWidget, wrapper_css_class="col-lg-6")
    directives.widget("picture", NamedImageFieldWidget, wrapper_css_class="col-lg-6")
    directives.widget("passport_image", NamedImageFieldWidget, wrapper_css_class="col-lg-6")

    # the following are only admin infos
    id = schema.TextLine(title=_("Customer Nr"), required=True)

    salutation_personal = schema.Bool(
        title=_("Personal Saluation"), required=False, default=False
    )
    salutation_letter = schema.TextLine(title=_("Salutation Letter"), required=False)
    payed = schema.Bool(title=_("Payed"), required=False, default=False)
    booking_nr = schema.TextLine(title=_("Booking Nr"), required=False)
    inactive = schema.Bool(title=_("Inactive"), required=False, default=False)

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
        instructor="cmf.ManagePortal",
        state="cmf.ManagePortal",
        qualification="cmf.ManagePortal",
        partner_type="cmf.ManagePortal",
    )
    directives.write_permission(
        id="cmf.ManagePortal",
        email="cmf.ManagePortal",
        booking_nr="cmf.ManagePortal",
        inactive="cmf.ManagePortal",
        salutation_personal="cmf.ManagePortal",
        salutation_letter="cmf.ManagePortal",
        payed="cmf.ManagePortal",
        instructor="cmf.ManagePortal",
        state="cmf.ManagePortal",
        qualification="cmf.ManagePortal",
        partner_type="cmf.ManagePortal",
    )

    # mark searchable fields
    textindexer.searchable(
        "first_name", "last_name", "email",
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
            "instructor",
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
