from collective.coursetool import _
from collective.coursetool.config import BASE_FOLDER_ID
from collective.coursetool.content.member import IRegistrationSchema
from dexterity.membrane.behavior.settings import IDexterityMembraneSettings
from plone import api
from plone.app.users.browser.register import RegistrationForm
from plone.app.users.schema import IRegisterSchema
from Products.CMFCore.utils import getToolByName
from Products.membrane.interfaces.utilities import IUserAdder
from Products.membrane.utils import getCurrentUserAdder
from Products.statusmessages.interfaces import IStatusMessage
from zope.globalrequest import getRequest
from zope.interface import implementer

import logging


class IRegistration(IRegistrationSchema, IRegisterSchema):
    """ combination of coursetool and plone schema """



class Registration(RegistrationForm):
    schema = IRegistration

    def _get_security_settings(self):
        """override plone settings with dexterity.membrane settings"""
        settings = super()._get_security_settings()

        class RegistrationSettingsProxy(object):
            # proxy class for overridden settings from membrane
            use_email_as_login = api.portal.get_registry_record(
                "use_email_as_username", interface=IDexterityMembraneSettings,
            )
            use_uuid_as_userid = api.portal.get_registry_record(
                "use_uuid_as_userid", interface=IDexterityMembraneSettings,
            )
            enable_user_pwd_choice = settings.enable_user_pwd_choice

        return RegistrationSettingsProxy()

    def applyProperties(self, userid, data):
        # do not set any properties for membrane user
        pass


@implementer(IUserAdder)
class CourseToolMemberAdder(object):

    def addUser(self, userid, password):
        request = getRequest()
        first_name = request.get("first_name")
        last_name = request.get("last_name")
        email = request.get("email")

        if not (first_name or last_name or email):
            return

        member_base = api.portal.get()[BASE_FOLDER_ID]["members"]
        obj = api.content.create(
            container=member_base,
            type="coursetool.member",
            id=userid,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        logging.info("Successfully added courstool.member %s" % obj.absolute_url(1))
