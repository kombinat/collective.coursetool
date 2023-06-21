"""Module where all interfaces, events and exceptions live."""
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ICollectiveCoursetoolLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IMember(Interface):
    """user marker"""


class ICourse(Interface):
    """course marker"""


class ILocation(Interface):
    """location marker"""


class IExam(Interface):
    """exam marker"""


class ICertificate(Interface):
    """certificate marker"""


class ICourseToolSettings(Interface):
    """registry settings"""


class ICourseToolBaseFolder(Interface):
    """marker for courstool base portal"""


class IUtils(Interface):
    def member_url(self):
        """get url of coursetool member for usermenu"""

    def member_export(self):
        """export memberdata as XLSX"""


class IImportingMembers(Interface):
    """marker for events"""
