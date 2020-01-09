# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import today

class TelefonTriage(Document):
	pass

@frappe.whitelist()
def creat_new_anfrage(mitgliedschaft=None, kontakt=None, adresse=None, kunde=None):
	#creat new anfrage
	anfrage = frappe.get_doc({
		"doctype": "Anfrage",
		"datum": today()
	})
	
	anfrage.insert(ignore_permissions=True)
	
	#If mitgliedschaft available, set link
	if mitgliedschaft:
		anfrage.update({
			'mitgliedschaft': mitgliedschaft
		})
		anfrage.save()
		
	#If adresse available, set link
	if adresse:
		anfrage.update({
			'patienten_adresse': adresse
		})
		anfrage.save()
		
	#If kontakt available, set link
	if kontakt:
		anfrage.update({
			'patienten_kontakt': kontakt
		})
		anfrage.save()
		
	#If kunde available, set link
	if kunde:
		anfrage.update({
			'patient': kunde
		})
		anfrage.save()
	
	return anfrage.name