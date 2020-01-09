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
	if kontakt.first_name and kontakt.last_name:
		html += kontakt.first_name + " " + kontakt.last_name + "<br>"
	if adresse.address_line1:
		html += adresse.address_line1 + "<br>"
	if adresse.address_line2:
		html += adresse.address_line2 + "<br>"
	if adresse.plz:
		html += adresse.plz
	if adresse.city:
		html += " " + adresse.city
	if adresse.kanton:
		html += " " + adresse.kanton + '<br><br>'
	else:
		html += '<br><br>'
	if kontakt.email_id:
		html += kontakt.email_id + "<br>"
	if kontakt.phone:
		html += kontakt.phone + "<br>"
	if kontakt.mobile_no:
		html += kontakt.mobile_no
	html += '</p></div>'
	
	return html
	
@frappe.whitelist()
def get_titelzeile(kontakt, adresse):
	kontakt = frappe.get_doc("Contact", kontakt)
	adresse = frappe.get_doc("Address", adresse)
	titelzeile = '<b>'
	if kontakt.verstorben == 1:
		titelzeile += kontakt.salutation + " "
		titelzeile += kontakt.first_name + " "
		titelzeile += kontakt.last_name + " (verstorben"
		if kontakt.verstorben_am:
			titelzeile += " am " + str(kontakt.verstorben_am) + "), "
		else:
			titelzeile += "), "
		if kontakt.geburtsdatum:
			titelzeile += "geboren am " + str(kontakt.geburtsdatum) + ", "
		titelzeile += adresse.address_line1 + " "
		titelzeile += adresse.plz + " "
		titelzeile += adresse.city + "</b>"
		return titelzeile
	else:
		titelzeile += kontakt.salutation + " "
		titelzeile += kontakt.first_name + " "
		titelzeile += kontakt.last_name + ", "
		if kontakt.geburtsdatum:
			titelzeile += "geboren am " + str(kontakt.geburtsdatum) + ", "
		titelzeile += adresse.address_line1 + " "
		titelzeile += adresse.plz + " "
		titelzeile += adresse.city + "</b>"
		return titelzeile