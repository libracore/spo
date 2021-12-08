# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Beratungsslot(Document):
	pass

@frappe.whitelist(allow_guest=True)
def get_slots(topic="Medizin"):
    available_slots = frappe.db.sql("""
        SELECT 
            `name`, 
            `topic` AS `title`, 
            `start`, 
            `end`
        FROM `tabBeratungsslot`
        WHERE `start` >= DATE_ADD(DATE(NOW()), INTERVAL 2 DAY)
          AND `status` = "frei"
          AND `topic` = "{topic}";""".format(topic=topic), as_dict=True)
          
    return available_slots
