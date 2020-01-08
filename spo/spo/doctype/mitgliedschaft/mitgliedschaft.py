# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Mitgliedschaft(Document):
	pass

	
@frappe.whitelist()
def create_invoice(mitgliedschaft):
	mitgliedschaft = frappe.get_doc("Mitgliedschaft", mitgliedschaft)
	invoice = frappe.get_doc({
		"doctype": "Sales Invoice",
		"customer": mitgliedschaft.mitglied,
		"company": "Gönnerverein",
		#"due_date": ,
		"items": [
			{
				"item_code": mitgliedschaft.mitgliedschafts_typ,
				"qty": 1,
				"cost_center": "Main - GöV"
			}
		]
	})
	invoice.insert()
	return invoice.name
	