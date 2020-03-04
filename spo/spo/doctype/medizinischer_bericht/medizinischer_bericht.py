# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MedizinischerBericht(Document):
	pass

@frappe.whitelist()
def get_deckblat_data(mandat):
	data = {}
	if mandat:
		mandat = frappe.get_doc("Mandat", mandat)
		if mandat.kontakt:
			patienten_kontakt = frappe.get_doc("Contact", mandat.kontakt)
			data["name_klient"] = patienten_kontakt.first_name + " " + patienten_kontakt.last_name
			data["geburtsdatum_klient"] = patienten_kontakt.geburtsdatum
		else:
			data["name_klient"] = ''
			data["geburtsdatum_klient"] = ''
		employee = frappe.db.sql("""SELECT `name` FROM `tabEmployee` WHERE `user_id` = '{owner}'""".format(owner=mandat.owner), as_dict=True)
		if len(employee) > 0:
			data["beraterin"] = employee[0].name
		else:
			data["beraterin"] = ''
		if mandat.rsv:
			data["rsv"] = mandat.rsv
		else:
			data["rsv"] = ''
		if mandat.rsv_kontakt:
			data["rsv_kontakt"] = mandat.rsv_kontakt
		else:
			data["rsv_kontakt"] = ''
			
		return data
	else:
		return False