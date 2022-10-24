from Products.membrane.testing import MEMBRANE_PROFILES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.coursetool


class CollectiveCoursetoolLayer(PloneSandboxLayer):

    defaultBases = (MEMBRANE_PROFILES_FIXTURE, PLONE_FIXTURE)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity

        self.loadZCML(package=plone.app.dexterity)

        import plone.restapi

        self.loadZCML(package=plone.restapi)

        self.loadZCML(package=collective.coursetool)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "collective.coursetool:default")


COLLECTIVE_COURSETOOL_FIXTURE = CollectiveCoursetoolLayer()


COLLECTIVE_COURSETOOL_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_COURSETOOL_FIXTURE,),
    name="CollectiveCoursetoolLayer:IntegrationTesting",
)


COLLECTIVE_COURSETOOL_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_COURSETOOL_FIXTURE,),
    name="CollectiveCoursetoolLayer:FunctionalTesting",
)


COLLECTIVE_COURSETOOL_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_COURSETOOL_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="CollectiveCoursetoolLayer:AcceptanceTesting",
)
