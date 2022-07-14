from collective.coursetool import _
from collective.coursetool.config import BASE_FOLDER_ID
from collective.coursetool.config import BASE_FOLDER_TITLE
from plone import api
from plone.protect.utils import addTokenToUrl
from zope.browsermenu.interfaces import IBrowserMenu
from zope.browsermenu.interfaces import IBrowserSubMenuItem
from zope.browsermenu.menu import BrowserMenu
from zope.browsermenu.menu import BrowserSubMenuItem
from zope.component import getAdapters
from zope.interface import implementer
from zope.interface import Interface


class ICoursetoolSubMenuItem(IBrowserSubMenuItem):
    """ menu item linking to coursetool menu """


class ICoursetoolMenu(IBrowserMenu):
    """ toolbar menu """


@implementer(ICoursetoolSubMenuItem)
class CoursetoolSubMenuItem(BrowserSubMenuItem):
    title = _(BASE_FOLDER_TITLE)
    short_title = _(BASE_FOLDER_TITLE)
    icon = "gear-wide-connected"
    submenuId = "collective_coursetoolmenu_actions"
    order = 60
    permission = "cmf.ManagePortal"

    @property
    def action(self):
        return self.context.absolute_url() + f"/{BASE_FOLDER_ID}"

    @property
    def extra(self):
        return {
            "id": "collective-coursetoolmenu",
            "disabled": False,
            "li_class": "",
        }

    def available(self):
        portal = api.portal.get()
        if BASE_FOLDER_ID not in portal:
            return False
        return super().available()


@implementer(ICoursetoolMenu)
class CoursetoolMenu(BrowserMenu):

    def getMenuItems(self, context, request):
        # simple listing of the coursetool base folder contents
        coursetool_base = api.portal.get()[BASE_FOLDER_ID]
        coursetool_listing = coursetool_base.restrictedTraverse("@@contentlisting")
        return [{
            "title": item.Title(),
            "description": item.Description(),
            "action": addTokenToUrl(item.getURL(), request),
            "selected": False,
            "icon": None,
            "extra": {
                "id": f"coursetool-view-{item.getId()}",
                "separator": None,
                "class": "",
                "modal": "",
            },
            "submenu": None,
        } for item in coursetool_listing()]
