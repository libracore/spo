# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns = [
		{"label": _("Mandat"), "fieldname": "Mandat", "fieldtype": "Data", "width": 150},
		{"label": _("Vorname"), "fieldname": "Vorname", "fieldtype": "Data", "width": 150},
		{"label": _("Nachname"), "fieldname": "Nachname", "fieldtype": "Data", "width": 150},
		{"label": _("Auftraggeber"), "fieldname": "Auftraggeber", "fieldtype": "Data", "width": 150},
		{"label": _("Referenz"), "fieldname": "Referenz", "fieldtype": "Data", "width": 150},
		{"label": _("Beraterin"), "fieldname": "Beraterin", "fieldtype": "Data", "width": 150}
	]
	data = frappe.db.sql("""SELECT
								`name`,
								`vorname`,
								`nachname`,
								`auftraggeber_name`,
								`rechtsschutz_ref`,
								`owner`
							FROM `tabMandat` WHERE `docstatus` = 0""", as_list=True)
	return columns, data
