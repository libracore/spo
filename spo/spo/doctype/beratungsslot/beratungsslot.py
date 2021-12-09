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
            `name` AS `id`, 
            `topic` AS `title`, 
            `start`, 
            `end`
        FROM `tabBeratungsslot`
        WHERE `start` >= DATE_ADD(DATE(NOW()), INTERVAL 2 DAY)
          AND `status` = "frei"
          AND `topic` = "{topic}";""".format(topic=topic), as_dict=True)
          
    return available_slots

@frappe.whitelist(allow_guest=True)
def reserve_slot(slot, member, first_name, last_name, address, 
    city, pincode, email, phone):
    # verify if this slot is still available
    available_slots = frappe.db.sql("""
        SELECT COUNT(`name`) AS `slots`
        FROM `tabBeratungsslot`
        WHERE `name` = "{slot}"
          AND `status` = "frei";""".format(slot=slot), as_dict=True)[0]['slots']
    if available_slots == 1:
        # slot available, reserve
        slot = frappe.get_doc("Beratungsslot", slot)
        slot.customer = member
        slot.first_name = first_name
        slot.last_name = last_name
        slot.address = address
        slot.city = city
        slot.pincode = pincode
        slot.email_id = email
        slot.phone = phone
        slot.status = "reserviert"
        slot.save(ignore_permissions=True)
        return True
    else:
        # already taken
        return False
