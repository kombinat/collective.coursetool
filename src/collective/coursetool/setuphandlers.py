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
        obj = api.content.create(
            container=_base,
            type="Folder",
            id="members",
            title=_("Members"),
        )
        obj.setLayout("listing_members")
        transaction.commit()

    if "courses" not in _base:
        obj = api.content.create(
            container=_base,
            type="Folder",
            id="courses",
            title=_("Courses"),
        )
        obj.setLayout("listing_courses")
        transaction.commit()

    if "exams" not in _base:
        obj = api.content.create(
            container=_base,
            type="Folder",
            id="exams",
            title=_("Exams"),
        )
        obj.setLayout("listing_exams")
        transaction.commit()

    if "certificates" not in _base:
        obj = api.content.create(
            container=_base,
            type="Folder",
            id="certificates",
            title=_("Certificates"),
        )
        obj.setLayout("listing_certificates")
        transaction.commit()


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.


def reload_profile(context):
    loadMigrationProfile(context, "profile-collective.coursetool:default")
