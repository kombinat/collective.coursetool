from collective.coursetool import _
from collective.coursetool.config import BASE_FOLDER_ID
from collective.coursetool.content.member import IMemberSchema
from datetime import datetime
from openpyxl import load_workbook
from plone import api
from plone.restapi.interfaces import IDeserializeFromJson
from Products.CMFPlone.utils import _createObjectByType
from zope.component import getMultiAdapter
from zope.publisher.browser import BrowserView

import logging
import transaction


log = logging.getLogger(__name__)


SCHEMA_MAPPING = {
    # schema name: excel col idx
    "id": 1,
    "salutation": 2,
    "graduation": 3,
    "lastname": 4,
    "firstname": 5,
    "address": 7,
    "address2": 6,
    "cty_code": 8,
    "zip_code": 9,
    "city": 10,
    "website": 11,
    "booking_nr": 12,
    "inactive": 13,
    "email": 14,
    "phone": 15,
    "mobile_phone": 16,
    "fax": 17,
    "birthday": 18,
    "salutation_letter": 21,
    "payed": 25,
    "payed_date": 26,
    "salutation_personal": 27,
}
VOCAB_MAPPING = {
    "state": 31,
    "qualification": 32,
    "partner_type": 33,
}
METADATA_MAPPING = {
    "created": 19,
    "modified": 20,
    "effective": 23,
    "expired": 24,
}
STATE_MAPPING = {
    "Eingelesen mit Befähigung": "read_qualified",
    "Eingelesen, KEINE Befähigung": "read_no_qualification",
    "Eingelesen, KEIN Geburtsdatum": "read_no_birthday",
    "Komplett, NICHT gedruckt": "complete_not_printed",
    "Komplett, gedruckt": "complete_printed",
    "Nicht Eingelesen": "not_read",
}


class ImportMembers(BrowserView):
    def __call__(self):
        if not self.request.get("import_data"):
            return self.index()

        _xlsx_file = self.request["import_data"]

        wb = load_workbook(_xlsx_file, read_only=True)
        ws = wb.active
        ws.reset_dimensions()

        schema_names = IMemberSchema.names()
        member_base = api.portal.get()[BASE_FOLDER_ID]["members"]

        # assume the first row columns are titles
        for num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 1):
            data = {}

            __traceback_info__ = row

            for fld, idx in SCHEMA_MAPPING.items():
                if fld not in schema_names or row[idx] is None:
                    continue
                if IMemberSchema[fld]._type == bool:
                    data[fld] = str(row[idx]).lower() == "true"
                elif IMemberSchema[fld]._type == str:
                    # force str
                    data[fld] = str(row[idx])
                elif isinstance(row[idx], datetime):
                    data[fld] = row[idx].strftime("%Y-%m-%d")
                else:
                    data[fld] = row[idx]

            for fld, idx in METADATA_MAPPING.items():
                if row[idx] is None:
                    continue
                data[fld] = row[idx].isoformat()

            for fld, idx in VOCAB_MAPPING.items():
                if len(row) <= idx or row[idx] is None:
                    continue
                if fld == "state":
                    data[fld] = STATE_MAPPING.get(row[idx], None)
                    continue
                data[fld] = [v.strip() for v in row[idx].split(",") if v]

            __traceback_info__ = data

            if data["id"] in member_base:
                obj = member_base[data["id"]]
            else:
                obj = api.content.create(
                    container=member_base,
                    type="coursetool.member",
                    id=data["id"],
                )

            deserializer = getMultiAdapter((obj, self.request), IDeserializeFromJson)
            obj = deserializer(validate_all=False, data=data)
            obj.reindexObject()

            log.info(f"{num} Imported data for {obj}")
            transaction.commit()

        api.portal.show_message(_("Imported members"), request=self.request)
        return self.index()
