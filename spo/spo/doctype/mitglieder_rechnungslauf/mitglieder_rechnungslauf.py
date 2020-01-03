# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import add_days, today
from spo.spo.doctype.mitgliedschaft.mitgliedschaft import create_invoice

class MitgliederRechnungslauf(Document):
	def before_save(self):
		vorlauf = frappe.get_doc("Einstellungen").rechnungslauf_vorlauf
		datum_inkl_vorlauf = add_days(today(), vorlauf)
		ablaufende_mitgliedschaften = frappe.db.sql("""SELECT `name`, `customer`, `mitgliedschafts_typ`, `ende` FROM `tabMitgliedschaft` WHERE `ende` <= '{datum_inkl_vorlauf}'
														AND `name` NOT IN (SELECT `mitgliedschaft` FROM `tabAuslaufende Mitgliedschaften`) LIMIT 500""".format(datum_inkl_vorlauf=datum_inkl_vorlauf), as_dict=True)
		for mitglied in ablaufende_mitgliedschaften:
			row = self.append('auslaufende_mitgliedschaften', {})
			row.mitgliedschaft = mitglied.name
			row.kunde = mitglied.customer
			row.type = mitglied.mitgliedschafts_typ
			row.ende = mitglied.ende
			
	def before_submit(self):
		for mitgliedschaft in self.auslaufende_mitgliedschaften:
			rechnung = create_invoice(mitgliedschaft.mitgliedschaft)
			mitgliedschaft = frappe.get_doc("Mitgliedschaft", mitgliedschaft.mitgliedschaft)
			mitgliedschaft.rechnung = rechnung
			mitgliedschaft.save()