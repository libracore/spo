# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = ["ID:Link/Anfrage", "Datum:Date", "Vorname:Date", "Nachname:Data", "Wohnort:Data", "Kanton:Data", "Erstellt von:Data", "Zuletzt bearbeitet von:Data"], []
	data = frappe.db.sql("""SELECT `name`, `datum`, `patient_vorname`, `patient_nachname`, `patient_ort`, `patient_kanton`, `owner`, `modified_by` FROM `tabAnfrage`""", as_list=True)
	return columns, data
