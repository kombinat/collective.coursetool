"""Module where all interfaces, events and exceptions live."""
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ICollectiveCoursetoolLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IMember(Interface):
    """user marker"""


class ICourse(Interface):
    """course marker"""


class IExam(Interface):
    """exam marker"""


class ICertificate(Interface):
    """certificate marker"""


class ICourseToolSettings(Interface):
    """registry settings"""


class ICourseToolBaseFolder(Interface):
    """marker for courstool base portal"""
