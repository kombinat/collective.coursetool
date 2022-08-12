from . import _
from bda.plone.shop.vocabularies import AVAILABLE_QUANTITY_UNITS


# patch quantity units vocabulary for empty value
_patched_AVAILABLE_QUANTITY_UNITS = AVAILABLE_QUANTITY_UNITS
_patched_AVAILABLE_QUANTITY_UNITS["members"] = _("Quantity Members")
