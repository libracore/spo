# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import formatdate

class MedizinischerBericht(Document):
	pass
	# def validate(self):
		# for ausgangslage in self.ausgangslage:
			# if ausgangslage.krankengeschichte:
				# ausgangslage.krankengeschichte = ausgangslage.krankengeschichte.replace("<br>", "")
				# ausgangslage.krankengeschichte = ausgangslage.krankengeschichte.replace("</div>", "<br>")
				# ausgangslage.krankengeschichte = ausgangslage.krankengeschichte.replace("<div>", "")
			# if ausgangslage.bemerkung:
				# ausgangslage.bemerkung = ausgangslage.bemerkung.replace("<br>", "")
				# ausgangslage.bemerkung = ausgangslage.bemerkung.replace("</div>", "<br>")
				# ausgangslage.bemerkung = ausgangslage.bemerkung.replace("<div>", "")
		# for korrespondenz in self.korrespondenz:
			# if korrespondenz.wortlaut:
				# korrespondenz.wortlaut = korrespondenz.wortlaut.replace("<br>", "")
				# korrespondenz.wortlaut = korrespondenz.wortlaut.replace("</div>", "<br>")
				# korrespondenz.wortlaut = korrespondenz.wortlaut.replace("<div>", "")
			# if korrespondenz.bemerkung:
				# korrespondenz.bemerkung = korrespondenz.bemerkung.replace("<br>", "")
				# korrespondenz.bemerkung = korrespondenz.bemerkung.replace("</div>", "<br>")
				# korrespondenz.bemerkung = korrespondenz.bemerkung.replace("<div>", "")

@frappe.whitelist()
def get_deckblat_data(mandat):
	data = {}
	if mandat:
		mandat = frappe.get_doc("Mandat", mandat)
		if mandat.kontakt:
			patienten_kontakt = frappe.get_doc("Contact", mandat.kontakt)
			data["name_klient"] = patienten_kontakt.first_name + " " + patienten_kontakt.last_name
			data["geburtsdatum_klient"] = formatdate(string_date=patienten_kontakt.geburtsdatum, format_string='dd.mm.yyyy')
		else:
			data["name_klient"] = ''
			data["geburtsdatum_klient"] = ''
		employee = frappe.db.sql("""SELECT `name` FROM `tabEmployee` WHERE `user_id` = '{owner}'""".format(owner=frappe.session.user), as_dict=True)
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