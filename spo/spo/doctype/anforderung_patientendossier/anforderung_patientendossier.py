# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AnforderungPatientendossier(Document):
	pass

@frappe.whitelist()
def get_kunden_data(kunde, adresse, kontakt):
	kunde = frappe.get_doc("Customer", kunde)
	adresse = frappe.get_doc("Address", adresse)
	kontakt = frappe.get_doc("Contact", kontakt)
	
	html = '<div><h4>Kunde:</h4><p>'
	html += kontakt.first_name + " " + kontakt.last_name + "<br>" or ''
	html += adresse.address_line1 + "<br>" or ''
	if adresse.address_line2:
		html += adresse.address_line2 + "<br>" or ''
	html += str(adresse.plz) + " " + adresse.city + " " + adresse.kanton + '<br><br>'
	html += kontakt.email_id + "<br>" or ''
	html += kontakt.phone + "<br>" or ''
	html += kontakt.mobile_no or ''
	html += '</p></div>'
	
	return html