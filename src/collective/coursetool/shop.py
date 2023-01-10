from bda.plone.orders.common import get_order
from plone import api


def payment_success(data):
    order = get_order(data.context, data.order_uid)
    uids = order.attrs.get("buyable_uids")
    if not uids:
        # should not happen
        return
    course = api.content.get(UID=uids[0])
    member = api.content.get(UID=order.attrs.get("creator"))
    api.relation.create(source=course, target=member, relationship="members")
