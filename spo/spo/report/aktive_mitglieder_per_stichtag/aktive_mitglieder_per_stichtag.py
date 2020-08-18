# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import getdate
from frappe import _

def execute(filters=None):
	columns, data = ["Mitgliedschaft:Link/Mitgliedschaft:150", "Mitglied:Link/Customer:150", "Typ:Data:100", "Rechnung:Link/Sales Invoice:150", "Betrag:Currency:80", "Ausstehend:Currency:80", "Status:Data:80", "Mahnstufe:Data:80"], []
	mitgliedschaften = frappe.db.sql("""SELECT `name`, `mitglied`, `mitgliedschafts_typ`, `rechnung` FROM `tabMitgliedschaft` WHERE DATE(`start`) <= '{stichtag}' AND DATE(`ende`) >= '{stichtag}'""".format(stichtag=filters.stichtag), as_dict=True)
	for mitgliedschaft in mitgliedschaften:
		data_to_append = []
		data_to_append.append(mitgliedschaft.name)
		data_to_append.append(mitgliedschaft.mitglied)
		data_to_append.append(mitgliedschaft.mitgliedschafts_typ)
		if mitgliedschaft.rechnung:
			data_to_append.append(mitgliedschaft.rechnung)
			rechnung = frappe.get_doc("Sales Invoice", mitgliedschaft.rechnung)
			data_to_append.append(rechnung.grand_total)
			data_to_append.append(rechnung.outstanding_amount)
			data_to_append.append(_(rechnung.status))
			data_to_append.append(rechnung.payment_reminder_level)
		else:
			data_to_append.append('---')
			data_to_append.append(0.00)
			data_to_append.append(0.00)
			data_to_append.append('Keine Rechnung')
			data_to_append.append(0)
		data.append(data_to_append)
		
	return columns, data
