from Acquisition import aq_inner
from collective.coursetool import _
from collective.coursetool.permissions import CoursetoolAdmin
from DateTime import DateTime
from io import BytesIO
from openpyxl import Workbook
from plone import api
from plone.base.batch import Batch
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.browser.view import DefaultView
from plone.memoize.instance import memoize
from plone.namedfile.file import NamedBlobImage
from plone.protect import PostOnly
from plone.protect import protect
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.interfaces import ISerializeToJson
from plone.z3cform import layout
from Products.CMFPlone.browser.search import munge_search_term
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

import logging
import pdf2image
import transaction


logger = logging.getLogger(__name__)


def pretty_date(val):
    return DateTime(val).strftime("%d.%m.%Y")


def pretty_datetime(val):
    return DateTime(val).strftime("%d.%m.%Y, %H:%M Uhr")


class ColumnDefinition(object):
    def __init__(self, label, f_attr, linked=False, formatter=None, sort_on=False):
        self.label = label
        self.f_attr = f_attr
        self.linked = linked
        self.formatter = formatter
        self.sort_on = sort_on

    def factory(self, obj):
        attr = getattr(obj.aq_base, self.f_attr, "-")
        if self.formatter and callable(self.formatter):
            attr = self.formatter(attr)
        if self.linked:
            return f"""<a href="{obj.absolute_url()}">{attr}</a>"""
        return attr


class ListingBase(BrowserView):
    portal_type = " - "
    row_count = True
    initial_sort_index = "sortable_title"
    initial_sort_order = "asc"

    def __init__(self, *args):
        super().__init__(*args)
        if self.request.get("clear"):
            self.request.set("SearchableText", "")

    @property
    def b_size(self):
        b_size = (
            getattr(self.request, "b_size", None)
            or getattr(self.request, "limit_display", None)
            or 50
        )
        return int(b_size)

    @property
    def b_start(self):
        b_start = getattr(self.request, "b_start", None) or 0
        return int(b_start)

    def results(self, **kwargs):
        kwargs.setdefault("portal_type", self.portal_type)
        kwargs.setdefault(
            "sort_on", self.request.get("sort_on", self.initial_sort_index)
        )
        kwargs.setdefault(
            "sort_order", self.request.get("sort_order", self.initial_sort_order)
        )
        kwargs.setdefault("batch", True)
        kwargs.setdefault("b_size", self.b_size)
        kwargs.setdefault("b_start", self.b_start)
        kwargs.setdefault("orphan", 1)

        # filtering
        if self.request.get("SearchableText") and self.request.get("search"):
            kwargs["SearchableText"] = munge_search_term(self.request["SearchableText"])

        listing = aq_inner(self.context).restrictedTraverse("@@contentlisting", None)
        if listing is None:
            return []

        results = listing(**kwargs)
        return results

    def batch(self):
        batch = Batch(self.results(), size=self.b_size, start=self.b_start, orphan=1)
        return batch

    def is_admin(self):
        return api.user.has_permission("Manage portal", obj=self.context)


class MembersListing(ListingBase):
    portal_type = "coursetool.member"
    row_count = False
    initial_sort_index = "customer_id"
    columns = [
        ColumnDefinition(_("Customer Nr"), "customer_id", True, sort_on="customer_id"),
        ColumnDefinition(_("Name"), "title", True, sort_on="sortable_title"),
        ColumnDefinition(_("Address"), "address_inline"),
        ColumnDefinition(_("EMail"), "email"),
        ColumnDefinition(_("Phone"), "phone"),
        ColumnDefinition(_("Mobile Phone"), "mobile_phone"),
    ]


class CoursesListing(ListingBase):
    portal_type = "coursetool.course"
    columns = [
        ColumnDefinition(_("Course-ID"), "id", sort_on="getId"),
        ColumnDefinition(_("Name"), "title", True, sort_on="sortable_title"),
        ColumnDefinition(_("City"), "location"),
    ]


class LocationsListing(ListingBase):
    portal_type = "coursetool.location"
    columns = [
        ColumnDefinition(_("Name"), "title", True),
        ColumnDefinition(_("City"), "city"),
    ]


class ExamsListing(ListingBase):
    portal_type = "coursetool.exam"
    columns = [
        ColumnDefinition(_("Name"), "title", True),
        ColumnDefinition(_("Exam date"), "date", formatter=pretty_datetime),
    ]


class CertificatesListing(ListingBase):
    portal_type = "coursetool.certificate"
    columns = [
        ColumnDefinition(_("Name"), "title", True),
    ]


class ViewBase(DefaultView):
    def render(self):
        # do not raise Exception, when no template is defined.
        if getattr(self, "index", None) is not None:
            return self.index()
        return "?"

    def can_edit(self):
        return api.user.has_permission("Modify portal content", obj=self.context)

    def is_admin(self):
        return api.user.has_permission("Manage portal", obj=self.context)


class CourseView(ViewBase):
    """ """

    @memoize
    def members(self):
        return [
            r.to_object
            for r in api.relation.get(source=self.context, relationship="members")
        ]

    member_objects = members

    def can_add_to_cart(self):
        if api.user.get_permissions().get(CoursetoolAdmin):
            # no cart widget for admins
            return False
        user = self.context.membrane_tool.getUserObject(
            api.user.get_current().getUserName()
        )
        return not user or user not in self.members()

    def all_members_mailaddress(self):
        mails = [m.email for m in self.members() if m.email]
        return ";".join(mails)


class ExamView(ViewBase):
    """ """

    def __call__(self):
        if self.request.get(
            "REQUEST_METHOD", "GET"
        ).upper() == "POST" and self.request.get("member_action"):
            action = self.request.get("member_action")
            factory = getattr(self, action, None)
            if factory and callable(factory):
                factory(self.request)
        return super().__call__()

    @memoize
    def members(self, mid=None):
        return [
            m
            for m in (self.context.members or [])
            if (
                mid is None
                or mid
                == (m["member"] if isinstance(m["member"], str) else m["member"].UID())
            )
        ]

    def member_objects(self):
        return [api.content.get(UID=m["member"].UID()) for m in self.members()]

    def can_add_to_cart(self):
        if api.user.get_permissions().get(CoursetoolAdmin):
            # no cart widget for admins
            return False
        user = self.context.membrane_tool.getUserObject(
            api.user.get_current().getUserName()
        )
        return not user or user.UID() not in self.context.members_uuids()

    def all_members_mailaddress(self):
        mails = [
            m["member"].email
            for m in self.members()
            if hasattr(m["member"], "email") and m["member"].email
        ]
        return ";".join(mails)

    @protect(PostOnly)
    def action_delete(self, REQUEST):
        _members = self.context.members

        for uid in REQUEST.get("uids", []):
            _members = [m for m in _members if m["member"] != uid]

        if len(_members) < len(self.context.members):
            self.context.members = _members
            self.context.reindexObject()
            transaction.commit()
            api.portal.show_message(_("Successfully deleted users."))
        else:
            api.portal.show_message(_("No action performed."))

    @protect(PostOnly)
    def action_exam_success(self, REQUEST):
        if self._update_members(REQUEST.get("uids", []), success=True):
            api.portal.show_message(_("Successfully changed users state."))
        else:
            api.portal.show_message(_("No action performed."))

    @protect(PostOnly)
    def action_exam_failed(self, REQUEST):
        if self._update_members(REQUEST.get("uids", []), success=False):
            api.portal.show_message(_("Successfully changed users state."))
        else:
            api.portal.show_message(_("No action performed."))

    @protect(PostOnly)
    def action_print(self, REQUEST):
        pdfs = []
        for uid in REQUEST.get("uids", []):
            member = api.content.get(UID=uid)
            view = PrintView(member, REQUEST)
            pdfs.append(view(download=False))
        return pdfs

    def _update_members(self, uids, success=False):
        _members = self.context.members
        _changes = False
        _types = self.context.types or ()
        for m in _members:
            if m["member"].UID() in uids:
                m["success"] = success
                m_obj = m["member"]
                m_exam_types = m_obj.exam_types or ()
                if success:
                    m_exam_types += _types
                else:
                    m_exam_types = tuple([q for q in m_exam_types if q not in _types])
                m_obj.exam_types = m_exam_types
                _changes = True
                transaction.commit()
        self.context.members = _members
        return _changes


class LocationView(ViewBase):
    """ """

    def courses(self):
        return [
            r.from_object
            for r in api.relation.get(target=self.context, relationship="location")
        ]


class MemberView(ViewBase):
    """ """

    def backrefs(self, key):
        return [
            r.from_object
            for r in api.relation.get(target=self.context, relationship="members")
            if r.from_object.portal_type == key
        ]

    def courses(self):
        return self.backrefs("coursetool.course")

    def exams(self):
        _ret = []

        for exam in self.context.portal_catalog(
            portal_type="coursetool.exam",
            members_uuids=self.context.UID(),
            sort_on="start",
        ):
            obj = exam.getObject()

            # filter for successful exams
            for e in ExamView(obj, self.request).members(mid=self.context.UID()):
                _ret.append(
                    dict(
                        url=obj.absolute_url(),
                        title=obj.title,
                        success=e["success"],
                    )
                )

        return _ret

    def certificates(self):
        return self.backrefs("coursetool.certificate")

    def documents(self):
        view = aq_inner(self.context).restrictedTraverse("@@contentlisting")
        return view()


class MemberEditForm(DefaultEditForm):
    css_class = "row"


MemberEditView = layout.wrap_form(MemberEditForm)


class PrintView(BrowserView):
    pdf_data = None
    filename = "card.pdf"

    def __call__(self, download=True):
        if not self.context.exam_types:
            api.portal.show_message(
                _("Member has no certificates or external qualifiaction."),
                type="error",
            )
            return self.request.response.redirect(self.context.absolute_url())

        # generate PDF content in your custom view
        self.update()
        self.save_preview()

        if download:
            self.request.response.setHeader(
                "Content-disposition", f"attachment; filename={self.filename}"
            )
            self.request.response.setHeader("Content-lengts", len(self.pdf_data))

        return self.pdf_data

    def update(self):
        # generate PDF content in your custom view and save it to self.pdf_data
        pass

    def save_preview(self):
        if self.pdf_data is None:
            # no pdf rendered
            return

        alsoProvides(self.request, IDisableCSRFProtection)

        try:
            preview = pdf2image.convert_from_bytes(self.pdf_data)
            png = BytesIO()
            png.name = self.filename.replace(".pdf", ".png")
            # save to BytesIO and convert to PNG
            preview[0].save(png)
            self.context.card_image = NamedBlobImage(
                data=png.getvalue(),
                contentType="image/png",
                filename=png.name,
            )
        except Exception as msg:
            logger.info(f"Could not save PDF preview: {msg}")


class CertificateView(ViewBase):
    """ """

    def members(self):
        return [
            r.to_object
            for r in api.relation.get(source=self.context, relationship="members")
        ]

    def can_add_to_cart(self):
        if api.user.get_permissions().get(CoursetoolAdmin):
            # no cart widget for admins
            return False
        # user = self.context.membrane_tool.getUserObject(api.user.get_current().getUserName())
        # return user and user.can_buy_certificate()
        return True


MEMBER_EXPORT_FIELDS = (
    "id",
    "customer_id",
    "salutation",
    "graduation",
    "first_name",
    "last_name",
    "address",
    "address2",
    "zip_code",
    "city",
    "cty_code",
    "email",
    "mobile_phone",
    "fax",
    "birthday",
    "salutation_personal",
    "salutation_letter",
    "pass_issue_date",
    "pass_expiration_date",
    "payed",
    "payed_date",
    "booking_nr",
    "inactive",
    "instructor",
    "state",
)


class Utils(BrowserView):
    def member(self):
        user = api.user.get_current()
        mbtool = self.context.membrane_tool
        uobj = None
        if user:
            uobj = mbtool.getUserObject(user.getUserName())
        return uobj

    def member_url(self):
        """get url of logged in member"""
        member = self.member()
        if member:
            return member.absolute_url()
        return ""

    def member_export(self):
        """export memberdata as XLSX"""
        try:
            members = api.content.get_view(
                name="view",
                context=self.context,
                request=self.request,
            ).member_objects()
        except Exception:
            api.portal.show_message(_("Members not found"))
            return self.request.response.redirect(self.context.absolute_url())

        wb = Workbook()
        ws = wb.active
        ws.title = "Members"

        ws.append(MEMBER_EXPORT_FIELDS)

        for mobj in members:
            serializer = getMultiAdapter((mobj, self.request), ISerializeToJson)
            item = serializer(include_items=False)
            __traceback_info__ = item
            _export_csv = []

            for _export_fld in MEMBER_EXPORT_FIELDS:
                _val = item.get(_export_fld, None)
                if _val is None:
                    _export_csv.append("")
                    continue
                if isinstance(_val, (list, tuple)):
                    _export_csv.append(f"{','.join(_val)}")
                    continue
                if isinstance(_val, dict):
                    _export_csv.append(f"{_val.get('title', '')}")
                    continue
                _export_csv.append(_val)

            ws.append(_export_csv)

        _out = BytesIO()
        wb.save(_out)

        self.request.response.setHeader(
            "Content-type",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.request.response.setHeader(
            "Content-disposition",
            f"attachment; filename={self.context.id}-members.xlsx",
        )
        self.request.response.setHeader("Pragma", "no-cache")

        return _out.getvalue()
