from collective.coursetool import _
from collective.coursetool.config import BASE_FOLDER_ID
from collective.coursetool.config import BASE_FOLDER_TITLE
from plone import api
from plone.app.upgrade.utils import loadMigrationProfile
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer

import transaction


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "collective.coursetool:uninstall",
        ]


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.
    portal = api.portal.get()

    # 1. create base folder
    if BASE_FOLDER_ID not in portal:
        api.content.create(
            container=portal,
            type="Folder",
            id=BASE_FOLDER_ID,
            title=_(BASE_FOLDER_TITLE),
        )
        transaction.commit()

    _base = portal[BASE_FOLDER_ID]
    _base.setLayout("coursetool_portal")

    if "members" not in _base:
        api.content.create(
            container=_base,
            type="Folder",
            id="members",
            title=_("Members"),
        )
        transaction.commit()

    if "courses" not in _base:
        api.content.create(
            container=_base,
            type="Folder",
            id="courses",
            title=_("Courses"),
        )
        transaction.commit()

    if "exams" not in _base:
        api.content.create(
            container=_base,
            type="Folder",
            id="exams",
            title=_("Exams"),
        )
        transaction.commit()

    if "certificates" not in _base:
        api.content.create(
            container=_base,
            type="Folder",
            id="certificates",
            title=_("Certificates"),
        )
        transaction.commit()


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.


def reload_profile(context):
    loadMigrationProfile(context, "profile-collective.coursetool:default")
