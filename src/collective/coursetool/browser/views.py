from Acquisition import aq_inner
from plone.base.batch import Batch
from Products.CMFPlone.browser.search import munge_search_term
from Products.Five import BrowserView


class ListingBase(BrowserView):
    portal_type = " - "

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
        if self.request.get("SearchableText"):
            kwargs["SearchableText"] = munge_search_term(self.request["SearchableText"])

        print(kwargs)
        listing = aq_inner(self.context).restrictedTraverse("@@folderListing", None)
        if listing is None:
            return []
        results = listing(**kwargs)
        return results

    def batch(self):
        batch = Batch(self.results(), size=self.b_size, start=self.b_start, orphan=1)
        return batch


class MembersListing(ListingBase):
    portal_type = "coursetool.member"
