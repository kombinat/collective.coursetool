from collective.coursetool.config import MEMBER_ID_FORMAT
from datetime import datetime
from plone import api
from random import randint

import hashlib


def generate_member_id():
    now = datetime.now().isoformat()
    return hashlib.md5(now.encode("utf-8")).hexdigest()


def generate_customer_id(random=False):
    if random:
        return MEMBER_ID_FORMAT.format(randint(0, 1e6))

    # import here in order to make the config value patchable by other
    # packages
    from collective.coursetool.config import MEMBER_ID_OFFSET

    # try to determine sequential user ID
    catalog = api.portal.get_tool("portal_catalog")
    members = catalog.unrestrictedSearchResults(
        portal_type="coursetool.member",
        sort_on="id",
        sort_order="reverse",
    )
    last_id = members and int(members[0].id) or 0
    if last_id < MEMBER_ID_OFFSET:
        last_id = MEMBER_ID_OFFSET
    return MEMBER_ID_FORMAT.format(last_id + 1)
