from Acquisition import aq_base
from collective.coursetool import _
from collective.coursetool.interfaces import IImportingMembers
from collective.coursetool.interfaces import IMember
from collective.coursetool.utils import generate_customer_id
from collective.coursetool.utils import generate_member_id
from dexterity.membrane.behavior.user import MembraneUserProperties
from dexterity.membrane.membrane_helpers import validate_unique_email
from plone.app.content.interfaces import INameFromTitle
from plone.app.dexterity import textindexer
from plone.app.users.schema import IRegisterSchema
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.app.z3cform.widget import DateFieldWidget
from plone.app.z3cform.widget import SelectFieldWidget
from plone.app.z3cform.widget import SingleCheckBoxBoolFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.formwidget.namedfile import NamedImageFieldWidget
from plone.indexer import indexer
from plone.namedfile import field as namedfile
from plone.schema.email import _isemail
from plone.schema.email import InvalidEmail
from plone.supermodel import model
from z3c.form.browser.text import TextFieldWidget
from z3c.form.interfaces import IEditForm
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Invalid
from zope.interface import invariant


def _validate_email(value):
    if _isemail(value):
        return True
    raise InvalidEmail(value)


class IRegistration(IRegisterSchema):
    first_name = schema.TextLine(title=_("Firstname"))
    last_name = schema.TextLine(title=_("Lastname"))
    email = schema.TextLine(title=_("Email"), constraint=_validate_email)
    birthday = schema.Date(title=_("Birthday"))

    address = schema.TextLine(title=_("Address"))
    zip_code = schema.TextLine(title=_("ZIP Code"))
    city = schema.TextLine(title=_("City"))
    cty_code = schema.TextLine(title=_("Country"))

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
    tac_agree = schema.Bool(
        title=_("Accept Terms and Conditions"),
        description=_("Please read our <a href=\"/agb\">Terms and Conditions</a>"),
        required=True,
    )

    directives.widget("first_name", TextFieldWidget, wrapper_css_class="col-lg-6")
    directives.widget("last_name", TextFieldWidget, wrapper_css_class="col-lg-6")
    directives.widget("email", TextFieldWidget, wrapper_css_class="col-lg-6")
    directives.widget("birthday", DateFieldWidget, wrapper_css_class="col-lg-6")
    directives.widget("zip_code", TextFieldWidget, wrapper_css_class="col-lg-2")
    directives.widget("city", TextFieldWidget, wrapper_css_class="col-lg-5")
    directives.widget("cty_code", TextFieldWidget, wrapper_css_class="col-lg-5")
    directives.widget("picture", NamedImageFieldWidget, wrapper_css_class="col-lg-6")
    directives.widget("passport_image", NamedImageFieldWidget, wrapper_css_class="col-lg-6")
    directives.widget("tac_agree", SingleCheckBoxBoolFieldWidget, wrapper_css_class="mt-5")


class IMemberSchema(model.Schema):
    """schema"""

    salutation = schema.Choice(
        title=_("Salutation"),
        vocabulary="bda.plone.shop.vocabularies.GenderVocabulary",
        required=False,
    )
    graduation = schema.TextLine(title=_("Graduation"), required=False)
    first_name = schema.TextLine(title=_("Firstname"), required=True)
    last_name = schema.TextLine(title=_("Lastname"), required=True)
    address = schema.TextLine(title=_("Address"), required=False)
    address2 = schema.TextLine(title=_("Address2"), required=False)
    zip_code = schema.TextLine(title=_("ZIP Code"), required=False)
    city = schema.TextLine(title=_("City"), required=False)
    cty_code = schema.TextLine(title=_("Country"), required=False)

    email = schema.ASCIILine(title=_("EMail"), required=False, constraint=_validate_email)
    website = schema.TextLine(title=_("Internet Address"), required=False)
    phone = schema.TextLine(title=_("Phone"), required=False)
    mobile_phone = schema.TextLine(title=_("Mobile Phone"), required=False)
    fax = schema.TextLine(title=_("Fax"), required=False)

    birthday = schema.Date(title=_("Birthday"), required=True)
    picture = namedfile.NamedBlobImage(
        title=_("User Image"),
        description=_("Upload your Passfoto (5MB max size)"),
        required=False,
    )
    passport_image = namedfile.NamedBlobImage(
        title=_("Passport Image"),
        description=_(
            "Please upload a foto of your passport "
            "to validate your identity."),
        required=False,
    )

    # this gets set by the PrintView if printed
    card_image = namedfile.NamedBlobImage(title=_("Card Image"), required=False)

    # layout wrapper CSS classes
    directives.widget("salutation", SelectFieldWidget, wrapper_css_class="col-lg-1")
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
    directives.widget("birthday", DateFieldWidget, wrapper_css_class="col-lg-6", _formater_length="long")
    directives.widget("picture", NamedImageFieldWidget, wrapper_css_class="col-lg-6")
    directives.widget("passport_image", NamedImageFieldWidget, wrapper_css_class="col-lg-6")
    directives.widget("card_image", NamedImageFieldWidget, wrapper_css_class="col-lg-6")

    username = schema.TextLine(
        title=_("Username"),
        required=False,
    )

    # the following are only admin infos
    customer_id = schema.TextLine(title=_("Customer Nr"), required=True)

    salutation_personal = schema.Bool(
        title=_("Personal Saluation"), required=False, default=False
    )
    salutation_letter = schema.TextLine(title=_("Salutation Letter"), required=False)
    pass_issue_date = schema.Date(title=_("Pass issued on"), required=False)
    pass_expiration_date = schema.Date(title=_("Pass expires on"), required=False)
    payed = schema.Bool(title=_("Payed"), required=False, default=False)
    payed_date = schema.Date(title=_("Payed on"), required=False)
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
        title=_("Qualifications"),
        value_type=schema.Choice(
            vocabulary="coursetool.vocabulary.memberqualifications",
        ),
        required=False,
        default=(),
    )
    directives.widget(
        "qualification",
        SelectFieldWidget,
        pattern_options={
            "allowNewItems": "false",
        },
    )

    exam_types = schema.Tuple(
        title=_("Exam Types"),
        value_type=schema.Choice(
            vocabulary="coursetool.vocabulary.examtypes",
        ),
        required=False,
        default=(),
    )
    directives.widget(
        "exam_types",
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

    admin_comment = schema.Text(
        title=_("Comment"),
        required=False,
    )

    # field visibility
    directives.omitted("customer_id", "username", "card_image")
    directives.no_omit(IEditForm, "customer_id", "card_image")

    # field permissions
    directives.read_permission(
        booking_nr="cmf.ManagePortal",
        inactive="cmf.ManagePortal",
        salutation_personal="cmf.ManagePortal",
        salutation_letter="cmf.ManagePortal",
        pass_issue_date="cmf.ManagePortal",
        pass_expiration_date="cmf.ManagePortal",
        payed="cmf.ManagePortal",
        payed_date="cmf.ManagePortal",
        instructor="cmf.ManagePortal",
        state="cmf.ManagePortal",
        qualification="cmf.ManagePortal",
        exam_types="cmf.ManagePortal",
        partner_type="cmf.ManagePortal",
        admin_comment="cmf.ManagePortal",
    )
    directives.write_permission(
        card_image="cmf.ManagePortal",
        customer_id="cmf.ManagePortal",
        email="cmf.ManagePortal",
        booking_nr="cmf.ManagePortal",
        inactive="cmf.ManagePortal",
        salutation_personal="cmf.ManagePortal",
        salutation_letter="cmf.ManagePortal",
        pass_issue_date="cmf.ManagePortal",
        pass_expiration_date="cmf.ManagePortal",
        payed="cmf.ManagePortal",
        payed_date="cmf.ManagePortal",
        instructor="cmf.ManagePortal",
        state="cmf.ManagePortal",
        qualification="cmf.ManagePortal",
        exam_types="cmf.ManagePortal",
        partner_type="cmf.ManagePortal",
        admin_comment="cmf.ManagePortal",
    )

    # mark searchable fields
    textindexer.searchable(
        "customer_id", "first_name", "last_name", "email",
    )

    model.fieldset(
        "metadata",
        label=_("Metadata"),
        fields=[
            "card_image",
            "customer_id",
            "booking_nr",
            "salutation_personal",
            "salutation_letter",
            "pass_issue_date",
            "pass_expiration_date",
            "payed",
            "payed_date",
            "state",
            "inactive",
            "instructor",
            "qualification",
            "exam_types",
            "partner_type",
            "admin_comment",
        ],
    )

    model.fieldset("membership", label=_("Membership"), fields=["username"])

    @invariant
    def email_unique(data):
        """The email must be unique, as it is the login name (user name).

        The tricky thing is to make sure editing a user and keeping
        his email the same actually works.
        """
        user = data.__context__
        if user is not None:
            if getattr(user, 'email', None) and user.email == data.email:
                # No change, fine.
                return
        error = validate_unique_email(data.email)
        if error:
            raise Invalid(error)


@implementer(IMember)
class Member(Container):
    """object"""

    @property
    def title(self):
        title_parts = [
            getattr(aq_base(self), "last_name", "-") or "-",
            getattr(aq_base(self), "first_name"),
        ]

        return " ".join([p for p in title_parts if p])

    @title.setter
    def title(self, value):
        pass

    def Title(self):
        return f"{self.customer_id}: {self.title}"

    def sortable_title(self):
        return self.title

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

    def can_buy_certificate():
        return True



@adapter(IMember)
class UserProperties(MembraneUserProperties):

    property_map = dict(
        gender="salutation",
        email="email",
        first_name="first_name",
        last_name="last_name",
        street="address",
        zip="zip_code",
        city="city",
        country="cty_code",
    )


@implementer(INameFromTitle)
@adapter(IMember)
class NameFromCreationDateEncrypted(object):

    def __new__(cls, context):
        instance = super().__new__(cls)
        instance.title = generate_member_id()
        return instance

    def __init__(self, context):
        pass


def new_customer_id(obj, event):

    if (
        IImportingMembers.providedBy(obj.REQUEST)
        or getattr(obj, "customer_id", None) is not None
    ):
        # customer_id is set during import
        return

    obj.customer_id = generate_customer_id()


@indexer(IMember)
def sortable_title(obj):
    return obj.title.lower().replace(" ", "_")
