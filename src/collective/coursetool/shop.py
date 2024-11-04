from bda.plone.checkout.interfaces import ICheckoutFormPresets
from bda.plone.orders.common import get_order
from bda.plone.shop.interfaces import IShopExtensionLayer
from collective.coursetool.browser.views import Utils
from collective.coursetool.interfaces import ICollectiveCoursetoolLayer
from node.utils import UNSET
from plone import api
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

import logging


logger = logging.getLogger(__name__)


def add_member_to_exam(exam, member):
    members = exam.members or []
    members.append({"member": member, "success": False})
    exam.members = members
    exam.reindexObject()


def payment_success(data):
    order = get_order(data.context, data.order_uid)
    uids = order.attrs.get("buyable_uids")
    if not uids:
        # should not happen
        return
    item = api.content.get(UID=uids[0])
    member = api.content.get(UID=order.attrs.get("creator"))
    api.relation.create(source=item, target=member, relationship="members")

    if item.portal_type == "coursetool.course":
        for exam in item.get_exams():
            if member.UID() in exam.members_uuids():
                # member is already in members
                continue
            add_member_to_exam(exam, member)

    if (
        item.portal_type == "coursetool.exam"
        and member.UID() not in item.members_uuids()
    ):
        add_member_to_exam(item, member)


CHECKOUT_FIELD_MAP = {
    "gender": "salutation",
    "firstname": "first_name",
    "lastname": "last_name",
    "street": "address",
    "zip": "zip_code",
    "country": "cty_code",
    "phone": ["mobile_phone", "phone"],
}


@implementer(ICheckoutFormPresets)
@adapter(Interface, ICollectiveCoursetoolLayer)
class CheckoutFormCourseMemberPresets(object):
    """Adapter to retrieve member presets for checkout form."""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        if api.user.is_anonymous():
            self.member = None
        else:
            self.member = Utils(context, request).member()

    def get_value(self, field_name):
        default = UNSET
        if self.member:
            parts = field_name.split(".")
            name = parts[-1]
            if "delivery_address" in parts:
                name = "delivery_%s" % name
            map_fld = CHECKOUT_FIELD_MAP.get(name, name)
            if isinstance(map_fld, list):
                for fld in map_fld:
                    default = getattr(self.member, fld, UNSET)
                    if default != UNSET:
                        break
            else:
                default = getattr(self.member, map_fld, UNSET)
        return default
