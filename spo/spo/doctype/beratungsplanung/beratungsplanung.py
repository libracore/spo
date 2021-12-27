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
            create_slot(date=slot.date , hour=slot.time, subject=slot.objective, consultant=slot.user)
            
        return


def create_slot(date, hour, subject, consultant):
    new_slot = frappe.get_doc({
        'doctype': 'Beratungsslot',
        'start': datetime.strptime("{0} {1}:00".format(date, hour), "%Y-%m-%d %H:%M"),
        'end': datetime.strptime("{0} {1}:30".format(date, hour), "%Y-%m-%d %H:%M"),
        'topic': subject,
        'user': user,
        'status': 'frei'
    })
    new_slot.insert()
    return
