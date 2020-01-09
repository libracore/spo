# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def cleanup_anfragen():
	anfragen = frappe.db.sql("""SELECT `name` FROM `tabAnfrage` WHERE `name` NOT IN (SELECT `spo_referenz` FROM `tabTimesheet Detail` WHERE `spo_dokument` = 'Anfrage')""", as_dict=True)
	for _anfrage in anfragen:
		anfrage = frappe.get_doc("Anfrage", _anfrage.name)
		anfrage.delete()