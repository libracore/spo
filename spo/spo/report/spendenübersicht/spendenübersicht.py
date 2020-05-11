# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import now_datetime
from frappe import _

def execute(filters=None):
	current_year = int(now_datetime().strftime('%Y'))
	last_year = current_year - 1
	second_last_year = current_year - 2
	third_last_year = current_year -  3
	fourth_last_year = current_year - 4
	fifth_last_year = current_year - 5
	
	columns, data = [
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer"},
		{"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data"},
		{"label": str(current_year), "fieldname": str(current_year), "fieldtype": "Float", "width": 100},
		{"label": str(last_year), "fieldname": str(last_year), "fieldtype": "Float", "width": 100},
		{"label": str(second_last_year), "fieldname": str(second_last_year), "fieldtype": "Float", "width": 100},
		{"label": str(third_last_year), "fieldname": str(third_last_year), "fieldtype": "Float", "width": 100},
		{"label": str(fourth_last_year), "fieldname": str(fourth_last_year), "fieldtype": "Float", "width": 100},
		{"label": str(fifth_last_year), "fieldname": str(fifth_last_year), "fieldtype": "Float", "width": 100},
		{"label": "Total {current_year} - {fifth_last_year}".format(current_year=current_year, fifth_last_year=fifth_last_year), "fieldname": "total", "fieldtype": "Float"}
	], []
	
	all_customer = frappe.db.sql("""SELECT `name`, `customer_name` FROM `tabCustomer`""", as_dict=True)
	
	for customer in all_customer:
		all_payment_entries_current = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND YEAR(`posting_date`) = '{year}'""".format(customer=customer.name, year=current_year)
		all_payment_entries_current_1 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND YEAR(`posting_date`) = '{year}'""".format(customer=customer.name, year=last_year)
		all_payment_entries_current_2 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND YEAR(`posting_date`) = '{year}'""".format(customer=customer.name, year=second_last_year)
		all_payment_entries_current_3 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND YEAR(`posting_date`) = '{year}'""".format(customer=customer.name, year=third_last_year)
		all_payment_entries_current_4 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND YEAR(`posting_date`) = '{year}'""".format(customer=customer.name, year=fourth_last_year)
		all_payment_entries_current_5 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND YEAR(`posting_date`) = '{year}'""".format(customer=customer.name, year=fifth_last_year)
		
		spende_current = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount' FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3000 - Einzelmitglieder - GöV', '3050 - Spenden - GöV')""".format(payment_query=all_payment_entries_current), as_dict=True)
		spende_current_1 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount'  FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3000 - Einzelmitglieder - GöV', '3050 - Spenden - GöV')""".format(payment_query=all_payment_entries_current_1), as_dict=True)
		spende_current_2 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount'  FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3000 - Einzelmitglieder - GöV', '3050 - Spenden - GöV')""".format(payment_query=all_payment_entries_current_2), as_dict=True)
		spende_current_3 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount'  FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3000 - Einzelmitglieder - GöV', '3050 - Spenden - GöV')""".format(payment_query=all_payment_entries_current_3), as_dict=True)
		spende_current_4 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount'  FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3000 - Einzelmitglieder - GöV', '3050 - Spenden - GöV')""".format(payment_query=all_payment_entries_current_4), as_dict=True)
		spende_current_5 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount'  FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3000 - Einzelmitglieder - GöV', '3050 - Spenden - GöV')""".format(payment_query=all_payment_entries_current_5), as_dict=True)
		
		total = 0
		
		_data = []
		_data.append(customer.name)
		_data.append(customer.customer_name)
		if spende_current[0].amount:
			_data.append(spende_current[0].amount * -1)
			total += spende_current[0].amount * -1
		else:
			_data.append('0.00')
		if spende_current_1[0].amount:
			_data.append(spende_current_1[0].amount * -1)
			total += spende_current_1[0].amount * -1
		else:
			_data.append('0.00')
		if spende_current_2[0].amount:
			_data.append(spende_current_2[0].amount * -1)
			total += spende_current_2[0].amount * -1
		else:
			_data.append('0.00')
		if spende_current_3[0].amount:
			_data.append(spende_current_3[0].amount * -1)
			total += spende_current_3[0].amount * -1
		else:
			_data.append('0.00')
		if spende_current_4[0].amount:
			_data.append(spende_current_4[0].amount * -1)
			total += spende_current_4[0].amount * -1
		else:
			_data.append('0.00')
		if spende_current_5[0].amount:
			_data.append(spende_current_5[0].amount * -1)
			total += spende_current_5[0].amount * -1
		else:
			_data.append('0.00')
		_data.append(total)
		data.append(_data)
	return columns, data
