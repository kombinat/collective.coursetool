from Acquisition import aq_inner
from collective.coursetool import _
from DateTime import DateTime
from plone import api
from plone.base.batch import Batch
from plone.dexterity.browser.view import DefaultView
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
        ColumnDefinition(_("PID"), "id"),
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

    def is_admin(self):
        return api.user.has_permission("Manage portal", obj=self.context)


class CourseView(ViewBase):
    """ """


class ExamView(ViewBase):
    """ """


class MemberView(ViewBase):
    """ """


class CertificateView(ViewBase):
    """ """
