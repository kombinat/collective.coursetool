"""Setup tests for this package."""
from collective.coursetool.testing import (  # noqa: E501,
    COLLECTIVE_COURSETOOL_INTEGRATION_TESTING,
)
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFPlone.utils import get_installer

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.coursetool is properly installed."""

    layer = COLLECTIVE_COURSETOOL_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])

    def test_product_installed(self):
        """Test if collective.coursetool is installed."""
        self.assertTrue(self.installer.is_product_installed("collective.coursetool"))

    def test_browserlayer(self):
        """Test that ICollectiveCoursetoolLayer is registered."""
        from collective.coursetool.interfaces import ICollectiveCoursetoolLayer
        from plone.browserlayer import utils

        self.assertIn(ICollectiveCoursetoolLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_COURSETOOL_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstall_product("collective.coursetool")
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if collective.coursetool is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed("collective.coursetool"))

    def test_browserlayer_removed(self):
        """Test that ICollectiveCoursetoolLayer is removed."""
        from collective.coursetool.interfaces import ICollectiveCoursetoolLayer
        from plone.browserlayer import utils

        self.assertNotIn(ICollectiveCoursetoolLayer, utils.registered_layers())
