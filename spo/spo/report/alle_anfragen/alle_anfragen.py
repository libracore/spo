# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [
		{"label": _("Anfrage"), "fieldname": "id", "fieldtype": "Link", "options": "Anfrage"},
		{"label": _("Datum"), "fieldname": "Datum", "fieldtype": "Date"},
		{"label": _("Vorname"), "fieldname": "Vorname", "fieldtype": "Data"},
		{"label": _("Nachname"), "fieldname": "Nachname", "fieldtype": "Data"},
		{"label": _("Wohnort"), "fieldname": "Wohnort", "fieldtype": "Data"},
		{"label": _("Kanton"), "fieldname": "Kanton", "fieldtype": "Data"},
		{"label": _("Erstellt von"), "fieldname": "Erstellt_von", "fieldtype": "Data"},
		{"label": _("Zuletzt bearbeitet von"), "fieldname": "zuletzt_bearbeitet_von", "fieldtype": "Data"}
	], []
	
	data = frappe.db.sql("""SELECT `name`, `datum`, `patient_vorname`, `patient_nachname`, `patient_ort`, `patient_kanton`, `owner`, `modified_by` FROM `tabAnfrage`""", as_list=True)
	#"ID:Link/Anfrage", "Datum:Date", "Vorname:Date", "Nachname:Data", "Wohnort:Data", "Kanton:Data", "Erstellt von:Data", "Zuletzt bearbeitet von:Data"
	return columns, data
