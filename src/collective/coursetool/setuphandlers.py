from collective.coursetool import _
from collective.coursetool.config import BASE_FOLDER_ID
from collective.coursetool.config import BASE_FOLDER_TITLE
from collective.coursetool.interfaces import ICourseToolBaseFolder
from plone import api
from plone.app.upgrade.utils import loadMigrationProfile
from plone.base.interfaces.constrains import ISelectableConstrainTypes
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import alsoProvides
from zope.interface import implementer

import transaction


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "collective.coursetool:uninstall",
        ]


def prepare_container(obj, tpl, constraints):
    obj.exclude_from_nav = True
    obj.setLayout(tpl)

    if constraints:
        constr = ISelectableConstrainTypes(obj)
        constr.setConstrainTypesMode(1)
        constr.setLocallyAllowedTypes(constraints)
        constr.setImmediatelyAddableTypes(constraints)


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
    alsoProvides(_base, ICourseToolBaseFolder)
    prepare_container(_base, "coursetool_portal", [])

    if "members" not in _base:
        obj = api.content.create(
            container=_base,
            type="Folder",
            id="members",
            title=_("Members"),
        )
        transaction.commit()
    else:
        obj = _base["members"]

    prepare_container(
        obj,
        "listing_members",
        [
            "coursetool.member",
        ],
    )

    if "courses" not in _base:
        obj = api.content.create(
            container=_base,
            type="Folder",
            id="courses",
            title=_("Courses"),
        )
        transaction.commit()
    else:
        obj = _base["courses"]

    prepare_container(
        obj,
        "listing_courses",
        [
            "coursetool.course",
        ],
    )

    if "exams" not in _base:
        obj = api.content.create(
            container=_base,
            type="Folder",
            id="exams",
            title=_("Exams"),
        )
        transaction.commit()
    else:
        obj = _base["exams"]

    prepare_container(
        obj,
        "listing_exams",
        [
            "coursetool.exam",
        ],
    )

    if "certificates" not in _base:
        obj = api.content.create(
            container=_base,
            type="Folder",
            id="certificates",
            title=_("Certificates"),
        )
        transaction.commit()
    else:
        obj = _base["certificates"]

    prepare_container(
        obj,
        "listing_certificates",
        [
            "coursetool.certificate",
        ],
    )

    # reload portlet import step to correctly apply blacklist
    context.portal_setup.runImportStepFromProfile(
        "profile-collective.coursetool:default",
        "portlets",
    )


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.


def reload_profile(context):
    loadMigrationProfile(context, "profile-collective.coursetool:default")
