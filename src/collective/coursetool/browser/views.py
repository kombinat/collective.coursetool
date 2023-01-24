from Acquisition import aq_inner
from collective.coursetool import _
from collective.coursetool.permissions import CoursetoolAdmin
from DateTime import DateTime
from plone import api
from plone.base.batch import Batch
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.browser.view import DefaultView
from plone.z3cform import layout
from Products.CMFPlone.browser.search import munge_search_term
from Products.Five import BrowserView


def pretty_date(val):
    return DateTime(val).strftime("%d.%m.%Y")


def pretty_datetime(val):
    return DateTime(val).strftime("%d.%m.%Y, %H:%M Uhr")


class ColumnDefinition(object):
    def __init__(self, label, f_attr, linked=False, formatter=None):
        self.label = label
        self.f_attr = f_attr
        self.linked = linked
        self.formatter = formatter

    def factory(self, obj):
        attr = getattr(obj, self.f_attr, "")
        if self.formatter:
            attr = self.formatter(attr)
        if self.linked:
            return f"""<a href="{obj.absolute_url()}">{attr}</a>"""
        return attr


class ListingBase(BrowserView):
    portal_type = " - "

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
        kwargs.setdefault("sort_on", self.request.get("sort_on", "sortable_title"))
        kwargs.setdefault("sort_order", self.request.get("sort_order", "asc"))
        kwargs.setdefault("batch", True)
        kwargs.setdefault("b_size", self.b_size)
        kwargs.setdefault("b_start", self.b_start)
        kwargs.setdefault("orphan", 1)

        # filtering
        if self.request.get("SearchableText") and self.request.get("search"):
            kwargs["SearchableText"] = munge_search_term(self.request["SearchableText"])

        listing = aq_inner(self.context).restrictedTraverse("@@folderListing", None)
        if listing is None:
            return []

        print(kwargs)
        results = listing(**kwargs)
        return results

    def batch(self):
        batch = Batch(self.results(), size=self.b_size, start=self.b_start, orphan=1)
        return batch

    def is_admin(self):
        return api.user.has_permission("Manage portal", obj=self.context)


class MembersListing(ListingBase):
    portal_type = "coursetool.member"
    columns = [
        ColumnDefinition(_("Name"), "title", True),
        ColumnDefinition(_("Address"), "address_inline"),
        ColumnDefinition(_("EMail"), "email"),
        ColumnDefinition(_("Phone"), "phone"),
        ColumnDefinition(_("Mobile Phone"), "mobile_phone"),
    ]


class CoursesListing(ListingBase):
    portal_type = "coursetool.course"
    columns = [
        ColumnDefinition(_("Course-ID"), "id"),
        ColumnDefinition(_("Name"), "title", True),
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
    def can_edit(self):
        return api.user.has_permission("Modify portal content", obj=self.context)

    def is_admin(self):
        return api.user.has_permission("Manage portal", obj=self.context)


class CourseView(ViewBase):
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
        user = self.context.membrane_tool.getUserObject(api.user.get_current().getUserName())
        return not user or user not in self.members()


class ExamView(ViewBase):
    """ """

    def members(self):
        for m in self.context.members:
            yield dict(
                member=api.content.get(UID=m["member"]),
                success="selected" in m["success"],
            )

    def can_add_to_cart(self):
        if api.user.get_permissions().get(CoursetoolAdmin):
            # no cart widget for admins
            return False
        user = self.context.membrane_tool.getUserObject(api.user.get_current().getUserName())
        return not user or user.UID() not in self.context.members_uuids()


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
        return [
            b.getObject() for b
            in self.context.portal_catalog(
                portal_type="coursetool.exam",
                members_uuid=self.context.UID(),
                sort_on="start",
            )
        ]

    def certificates(self):
        return self.backrefs("coursetool.certificate")


class MemberEditForm(DefaultEditForm):
    css_class = "row"


MemberEditView = layout.wrap_form(MemberEditForm)


class CertificateView(ViewBase):
    """ """

    def members(self):
        return [
            r.to_object
            for r in api.relation.get(source=self.context, relationship="members")
        ]


class Utils(BrowserView):

    def member_url(self):
        """ get url of logged in member """
        user = api.user.get_current()
        mbtool = self.context.membrane_tool
        if user:
            uobj = mbtool.getUserObject(user.getUserName())
            return uobj.absolute_url() if uobj else ""
        return ""
