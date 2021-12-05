# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Beratungsslot(Document):
	pass

@frappe.whitelist(allow_guest=True)
def get_slots():
    slots = [
        {'title': 'Beratung', 'start': '2021-12-06T08:00:00', 'end': '2021-12-06T08:30:00'},
        {'title': 'Beratung', 'start': '2021-12-06T09:00:00', 'end': '2021-12-06T09:30:00'},
        {'title': 'Beratung', 'start': '2021-12-06T10:00:00', 'end': '2021-12-06T10:30:00'},
    ]
    return slots
