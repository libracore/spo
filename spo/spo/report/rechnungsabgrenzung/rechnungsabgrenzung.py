# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import getdate, date_diff
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
		{"label": _("Grand Total"), "fieldname": "outstading_amount", "fieldtype": "Currency", 'width': 150},
		{"label": _("Betrag ") + year_1, "fieldname": "outstading_amount_year_1", "fieldtype": "Currency", 'width': 150},
		{"label": _("Betrag ") + year_2, "fieldname": "outstading_amount_year_2", "fieldtype": "Currency", 'width': 150}
	]
	
def get_data(filters):
	data = []
	total_year_days = 365
	total_year_1 = 0
	total_year_2 = 0
	total_amount = 0
	if filters.stichtag:
		start_year_1 = str(getdate(filters.stichtag).year) + '-01-01'
		end_year_1 = str(getdate(filters.stichtag).year) + '-12-31'
		
	sinvs = frappe.db.sql("""SELECT `name`, `customer`, `customer_name`, `grand_total`, `posting_date`
								FROM `tabSales Invoice`
								WHERE `docstatus` = 1
								AND `posting_date` >= '{start_year_1}'
								AND `posting_date` <= '{end_year_1}'
								AND `grand_total` > 0
								AND `company` = '{company}'""".format(start_year_1=start_year_1, end_year_1=end_year_1, company=filters.company), as_dict=True)
	
	for sinv in sinvs:
		days_in_year_1 = date_diff(end_year_1, sinv.posting_date)
		days_in_year_2 = total_year_days - days_in_year_1
		amount_year_1 = (sinv.grand_total / total_year_days) * days_in_year_1
		amount_year_2 = (sinv.grand_total / total_year_days) * days_in_year_2
		total_year_1 += amount_year_1
		total_year_2 += amount_year_2
		total_amount += sinv.grand_total
		data.append([sinv.name, sinv.customer, sinv.customer_name, sinv.grand_total, amount_year_1, amount_year_2])
	
		
	data.append(['', '', 'Total', total_amount, total_year_1, total_year_2])
	return data