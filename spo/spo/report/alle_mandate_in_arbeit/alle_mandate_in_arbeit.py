# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	columns = ['Mandat:Data:150', 'Vorname:Data:150', 'Nachname:Data:150', 'Auftraggeber:Data:150', 'Referenz:Data:150', 'Beraterin:Data:150']
	data = frappe.db.sql("""SELECT
								`name`,
								`vorname`,
								`nachname`,
								`auftraggeber_name`,
								`rechtsschutz_ref`,
								`owner`
							FROM `tabMandat`""", as_list=True)
	return columns, data
