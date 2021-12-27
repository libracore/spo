# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime

class Beratungsplanung(Document):
    def on_submit(self):
        # create slots from child table
        for slot in self.sloteingaben:
            # separate time blocks (field is in "10+11" format
            times = slot.time.split("+")
            for t in times:
                create_slot(date=slot.date , hour=t, subject=slot.objective, user=slot.user)
        
        frappe.db.commit()
        return


def create_slot(date, hour, subject, user):
    new_slot = frappe.get_doc({
        'doctype': 'Beratungsslot',
        'start': "{0} {1}:00:00".format(date, hour),
        'end': "{0} {1}:30:00".format(date, hour),
        'topic': subject,
        'user': user,
        'status': 'frei'
    })
    frappe.log_error("{0}".format(new_slot.as_dict()))
    new_slot.insert()
    return
