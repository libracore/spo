# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import getdate
from frappe import _

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data
	
def get_columns(filters):
	if filters.stichtag:
		year_1 = str(getdate(filters.stichtag).year)
		year_2 = str((getdate(filters.stichtag).year + 1))
	else:
		year_1 = 'bitte Stichtag wählen'
		year_2 = 'bitte Stichtag wählen'
		
	return [
		{"label": _("Sales Invoice"), "fieldname": "sinv", "fieldtype": "Link", "options": "Sales Invoice"},
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer"},
		{"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", 'width': 150},
		{"label": _("Ausstehender Betrag"), "fieldname": "outstading_amount", "fieldtype": "Currency", 'width': 150},
		{"label": _("Betrag ") + year_1, "fieldname": "outstading_amount_year_1", "fieldtype": "Currency", 'width': 150},
		{"label": _("Betrag ") + year_2, "fieldname": "outstading_amount_year_2", "fieldtype": "Currency", 'width': 150}
	]
	
def get_data(filters):
	if filters.stichtag:
		year_1 = str(getdate(filters.stichtag).year) + '-01-01'
		year_2 = str(getdate(filters.stichtag).year) + '-12-31'
		
	sinvs = frappe.db.sql("""SELECT `name`, `customer`, `customer_name`, `outstanding_amount`, `outstanding_amount`/2, `outstanding_amount`/2
								FROM `tabSales Invoice`
								WHERE `docstatus` = 1
								AND `posting_date` >= '{year_1}'
								AND `posting_date` <= '{year_2}'
								AND `outstanding_amount` > 0
								AND `company` = '{company}'""".format(year_1=year_1, year_2=year_2, company=filters.company), as_list=True)
								
	total = frappe.db.sql("""SELECT SUM(`outstanding_amount`)
								FROM `tabSales Invoice`
								WHERE `docstatus` = 1
								AND `posting_date` >= '{year_1}'
								AND `posting_date` <= '{year_2}'
								AND `outstanding_amount` > 0
								AND `company` = '{company}'""".format(year_1=year_1, year_2=year_2, company=filters.company), as_list=True)[0][0]
		
	sinvs.append(['', '', 'Total', total, (total/2), (total/2)])
	return sinvs