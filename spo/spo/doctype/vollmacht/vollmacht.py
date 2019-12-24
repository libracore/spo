# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Vollmacht(Document):
	pass

@frappe.whitelist()
def check_todesfall(mandat):
	mandat = frappe.get_doc("Mandat", mandat)
	if mandat.anfragen:
		anfrage = frappe.get_doc("Anfrage", mandat.anfragen)
		if anfrage.todesfall == 'Ja':
			return 1
		else:
			return 0
	else:
		return 0
	
@frappe.whitelist()
def get_kunden_data(kunde, adresse, kontakt):
	kunde = frappe.get_doc("Customer", kunde)
	adresse = frappe.get_doc("Address", adresse)
	kontakt = frappe.get_doc("Contact", kontakt)
	
	html = '<div><h4>Kunde:</h4><p>'
	html += kontakt.first_name + " " + kontakt.last_name + "<br>"
	html += adresse.address_line1 + "<br>"
	if adresse.address_line2:
		html += adresse.address_line2 + "<br>"
	html += str(adresse.plz) + " " + adresse.city + " " + adresse.kanton + '<br><br>'
	html += kontakt.email_id + "<br>" or ''
	html += kontakt.phone + "<br>" or ''
	html += kontakt.mobile_no or ''
	html += '</p></div>'
	
	return html
	
@frappe.whitelist()
def get_ang_data(ang, adresse, kontakt):
	kunde = frappe.get_doc("Customer", ang)
	adresse = frappe.get_doc("Address", adresse)
	kontakt = frappe.get_doc("Contact", kontakt)
	
	html = '<div><h4>Angehörige:</h4><p>'
	html += kontakt.first_name + " " + kontakt.last_name + "<br>"
	html += adresse.address_line1 + "<br>"
	if adresse.address_line2:
		html += adresse.address_line2 + "<br>"
	html += str(adresse.plz) + " " + adresse.city + " " + adresse.kanton + '<br><br>'
	html += kontakt.email_id + "<br>" or ''
	html += kontakt.phone + "<br>" or ''
	html += kontakt.mobile_no or ''
	html += '</p></div>'
	
	return html
	
@frappe.whitelist()
def get_fetching_data(adresse, kontakt):
	adresse = frappe.get_doc("Address", adresse)
	kontakt = frappe.get_doc("Contact", kontakt)
	
	return {
		'adresse': adresse,
		'kontakt': kontakt
		}