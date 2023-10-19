from plone import api
from plone.app.upgrade.utils import loadMigrationProfile

import logging
import transaction

logger = logging.getLogger(__name__)


def resync_workflow_state(context):
    catalog = api.portal.get_tool("portal_catalog")
    items = catalog(portal_type=["coursetool.course", "coursetool.exam"])
    _all = len(items)
    _old_state = {}

    for it in items:
        _old_state[it.UID] = it.review_state

    # reload profile to set new workflow
    loadMigrationProfile(context, "profile-collective.coursetool:default")
    wftool = api.portal.get_tool("portal_workflow")
    count = wftool.updateRoleMappings()
    logger.info(f"Updated {count} role mappings.")
    transaction.commit()

    for idx, it in enumerate(items, 1):
        obj = it.getObject()
        old_state = _old_state[it.UID]

        if (
            wftool.getInfoFor(obj, "review_state") == "private"
            and old_state == "published"
        ):
            wftool.doActionFor(obj, "publish")
            obj.reindexObject(idxs=["suppress_notifyModified"])
            transaction.commit()
            logger.info(f"{idx}/{_all} synced state {old_state} for {it.getPath()}")
