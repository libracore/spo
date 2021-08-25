# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Meldestelle(Document):
	pass


@frappe.whitelist(allow_guest=True)
def new_request():
    try:
        data = frappe.local.form_dict
        nr = frappe.get_doc({
            "doctype": "Meldestelle",
            "mandant": data.mandant,
            "report_from": data.fname + " " + data.lname,
            "phone": data.phone,
            "email": data.email,
            "availability": data.availability,
            "report": data.report
        })
        nr.insert(ignore_permissions=True)
        return True
    except:
        return False
