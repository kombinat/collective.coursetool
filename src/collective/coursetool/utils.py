from plone import api
from random import randint


def generate_courstool_member_id(random=True):
    if random:
        return f"{randint(0, 1e6):06d}"

    # try to determine sequential user ID
    catalog = api.portal.get_tool("portal_catalog")
    members = catalog.unrestrictedSearchResults(
        portal_type="coursetool.member",
        sort_on="id",
        sort_order="reverse",
    )
    last_id = members and int(members[0].id) or 0
    return f"{(last_id + 1):06d}"
