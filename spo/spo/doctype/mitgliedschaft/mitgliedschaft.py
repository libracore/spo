# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import add_days, today
from spo.utils import esr

class Mitgliedschaft(Document):
	pass

	
@frappe.whitelist()
def create_invoice(mitgliedschaft):
	mitgliedschaft = frappe.get_doc("Mitgliedschaft", mitgliedschaft)
	zahlungsziel = add_days(today(), frappe.get_doc("Einstellungen").rechnungslauf_zahlungsfrist)
	invoice = frappe.get_doc({
		"doctype": "Sales Invoice",
		"customer": mitgliedschaft.mitglied,
		"company": "Gönnerverein",
		"due_date": zahlungsziel,
		"items": [
			{
				"item_code": mitgliedschaft.mitgliedschafts_typ,
				"qty": 1,
				"description": frappe.utils.get_datetime(mitgliedschaft.start).strftime('%d.%m.%Y') + " - " + frappe.utils.get_datetime(mitgliedschaft.ende).strftime('%d.%m.%Y'),
				"cost_center": "Main - GöV"
			}
		]
	})
	invoice.insert()
	
	referencenumber = mitgliedschaft.mitglied.split("-")[2] + "00000" + invoice.name.split("-")[1] + invoice.name.split("-")[2] 
	invoice.update({
		"esr_reference": esr.get_reference_number(referencenumber),
		"esr_code": esr.generateCodeline(invoice.grand_total, referencenumber, "012000272")
	})
	invoice.save(ignore_permissions=True)
	
	return invoice.name
	