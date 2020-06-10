# -*- coding: utf-8 -*-
# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class FacharztBericht(Document):
	pass

@frappe.whitelist()
def get_adressat(facharzt=None, facharzt_name=None, kontakt=None, adresse=None):
	if facharzt:
		if kontakt:
			kontakt = frappe.get_doc("Contact", kontakt)
		else:
			try:
				_kontakt = frappe.get_all('Dynamic Link', filters={'link_doctype': 'Customer', 'link_name': facharzt, 'parenttype': 'Contact'}, fields=['parent'])[0].parent
				kontakt = frappe.get_doc("Contact", _kontakt)
			except:
				kontakt = None
		if adresse:
			adresse = frappe.get_doc("Address", adresse)
		else:
			try:
				_adresse = frappe.get_all('Dynamic Link', filters={'link_doctype': 'Customer', 'link_name': facharzt, 'parenttype': 'Address'}, fields=['parent'])[0].parent
				adresse = frappe.get_doc("Address", _adresse)
			except:
				adresse = None
				
		adressat = ''
		if kontakt:
			adressat += kontakt.salutation + "\n"
			adressat += kontakt.first_name + " " + kontakt.last_name + "\n"
		else:
			adressat += facharzt_name + "\n"
		if adresse:
			adressat += adresse.address_line1 + "\n"
			if adresse.address_line2:
				adressat += adresse.address_line2 + "\n"
			adressat += adresse.plz + " " + adresse.city + "\n"
		return adressat
	return False