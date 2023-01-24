from collective.coursetool import _
from collective.coursetool.config import BASE_FOLDER_ID
from collective.coursetool.content.member import IRegistration
from collective.coursetool.utils import generate_courstool_member_id
from dexterity.membrane.behavior.settings import IDexterityMembraneSettings
from plone import api
from plone.app.users.browser.register import RegistrationForm
from Products.CMFCore.utils import getToolByName
from Products.membrane.interfaces.utilities import IUserAdder
from Products.membrane.utils import getCurrentUserAdder
from Products.statusmessages.interfaces import IStatusMessage
from ZODB.POSException import ConflictError
from zope.component import getMultiAdapter
from zope.interface import implementer

import logging
import transaction


class Registration(RegistrationForm):

    schema = IRegistration

    def _get_security_settings(self):
        """override plone settings with dexterity.membrane settings"""
        settings = super()._get_security_settings()

        class RegistrationSettingsProxy(object):
            # proxy class for overridden settings from membrane
            use_email_as_login = api.portal.get_registry_record(
                "use_email_as_username",
                interface=IDexterityMembraneSettings,
            )
            use_uuid_as_userid = api.portal.get_registry_record(
                "use_uuid_as_userid",
                interface=IDexterityMembraneSettings,
            )
            enable_user_pwd_choice = settings.enable_user_pwd_choice

        return RegistrationSettingsProxy()

    def handle_join_success(self, data):
        # portal should be acquisition wrapped, this is needed for the schema
        # adapter below
        portal = getToolByName(self.context, "portal_url").getPortalObject()
        registration = getToolByName(self.context, "portal_registration")

        # user_id and login_name should be in the data, but let's be safe.
        user_id = data.get("user_id", data.get("username"))
        login_name = data.pop("login_name", data.get("username"))

        # Set the username for good measure, as some code may expect
        # it to exist and contain the user id.
        data["username"] = user_id

        # The login name may already be in the form, but not
        # necessarily, for example when using email as login.  This is
        # at least needed for logging in immediately when password
        # reset is bypassed.  We need the login name here, not the
        # user id.
        self.request.form["form.username"] = login_name

        password = data.get("password") or registration.generatePassword()

        try:
            adder = getCurrentUserAdder(self)
            new_user_id = adder.addUser(login_name, password, **data)
        except (AttributeError, ValueError) as err:
            logging.exception(err)
            IStatusMessage(self.request).addStatusMessage(err, type="error")
            self._finishedRegister = False
            return

        settings = self._get_security_settings()
        self._finishedRegister = True
        if data.get("mail_me") or (
            not settings.enable_user_pwd_choice and not data.get("password")
        ):
            # We want to validate the email address (users cannot
            # select their own passwords on the register form) or the
            # admin has explicitly requested to send an email on the
            # 'add new user' form.
            try:
                # When all goes well, this call actually returns the
                # rendered mail_password_response template.  As a side
                # effect, this removes any status messages added to
                # the request so far, as they are already shown in
                # this template.
                response = registration.registeredNotify(new_user_id)
                return response
            except ConflictError:
                # Let Zope handle this exception.
                raise
            except Exception as err:
                logging.exception(err)
                ctrlOverview = getMultiAdapter(
                    (portal, self.request), name="overview-controlpanel"
                )
                mail_settings_correct = not ctrlOverview.mailhost_warning()
                if mail_settings_correct:
                    # The email settings are correct, so the most
                    # likely cause of an error is a wrong email
                    # address.  We remove the account:
                    # Remove the account:
                    self.context.acl_users.userFolderDelUsers(
                        [new_user_id], REQUEST=self.request
                    )
                    self._finishedRegister = False
                    IStatusMessage(self.request).addStatusMessage(
                        _(
                            "status_fatal_password_mail",
                            default="Failed to create your account: we were "
                            "unable to send instructions for setting a password "
                            "to your email address: ${address}",
                            mapping={"address": data.get("email", "")},
                        ),
                        type="error",
                    )
                else:
                    # This should only happen when an admin registers
                    # a user.  The admin should have seen a warning
                    # already, but we warn again for clarity.
                    IStatusMessage(self.request).addStatusMessage(
                        _(
                            "status_nonfatal_password_mail",
                            default="This account has been created, but we "
                            "were unable to send instructions for setting a "
                            "password to this email address: ${address}",
                            mapping={"address": data.get("email", "")},
                        ),
                        type="warning",
                    )


@implementer(IUserAdder)
class CourseToolMemberAdder(object):
    def addUser(self, login_name, password, **data):
        member_base = api.portal.get()[BASE_FOLDER_ID]["members"]
        # generate random 6 digit user id
        userid = generate_courstool_member_id()
        id_gen_count = 0

        while userid in member_base:
            # if sequential ID is already there, generate a random one
            userid = generate_courstool_member_id()
            id_gen_count += 1
            if id_gen_count > 10:
                raise Exception("Could not generate UserID")

        with api.env.adopt_roles(["Manager", ]):
            obj = api.content.create(
                container=member_base,
                type="coursetool.member",
                id=userid,
                first_name=data.get("first_name", "Maximiliane"),
                last_name=data.get("last_name", "Muster"),
                email=login_name,
                picture=data.get("picture", None),
                passport_image=data.get("passport_image", None),
            )
            # set workflow state to "enabled"
            api.content.transition(obj, to_state="enabled")

            transaction.commit()

        logging.info("Successfully added coursetool.member %s" % obj.absolute_url(1))
        return obj.UID()
