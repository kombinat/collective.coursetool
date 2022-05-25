from plone.app.upgrade.utils import loadMigrationProfile
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


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

    # 1. create base folder


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.


def reload_profile(context):
    loadMigrationProfile(context, "profile-led.content:default")
