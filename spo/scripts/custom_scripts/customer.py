# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import nowdate, add_years, now_datetime
from frappe import _

@frappe.whitelist()
def check_contact(customer):
	customer = frappe.get_doc("Customer", customer)
	linked_contact = frappe.db.sql("""SELECT `name` FROM `tabContact` WHERE `name` = (SELECT `parent` FROM `tabDynamic Link` WHERE `link_doctype` = 'Customer' AND `link_name` = '{customer_name}' AND `parenttype` = 'Contact' LIMIT 1)""".format(customer_name=customer.name), as_list=True)
	if linked_contact:
		check_name(customer, linked_contact[0][0])
	else:
		create_contact(customer)
		
def check_name(customer, contact):
	contact = frappe.get_doc("Contact", contact)
	soll_fullname = contact.first_name + " " + contact.last_name
	if customer.customer_name != soll_fullname:
		customer.update({
			"customer_name": soll_fullname
		})
		customer.save()

def create_contact(customer):
	contact = frappe.get_doc({
		"doctype": "Contact",
		"first_name": customer.customer_name.split(" ")[0],
		"last_name": customer.customer_name.split(" ")[1],
		"links": [
			{
				"link_doctype": "Customer",
				"link_name": customer.name
			}
		]
	})
	contact.insert()
	
	
@frappe.whitelist()
def create_mitgliedschaft(customer):
	mitgliedschaft = frappe.get_doc({
		"doctype": "Mitgliedschaft",
		"mitglied": customer,
		"start": nowdate(),
		"ende": add_years(nowdate(), 1)
	})
	mitgliedschaft.insert()
	return mitgliedschaft.name
	
@frappe.whitelist()
def create_anfrage(customer):
	anfrage = frappe.get_doc({
		"doctype": "Anfrage",
		"mitglied": customer
	})
	anfrage.insert()
	return anfrage.name
	
@frappe.whitelist()
def create_mandat(customer):
	mandat = frappe.get_doc({
		"doctype": "Mandat",
		"mitglied": customer
	})
	mandat.insert()
	return mandat.name
	
@frappe.whitelist()
def get_spenden(customer):
	current_year = int(now_datetime().strftime('%Y'))
	last_year = current_year - 1
	second_last_year = current_year - 2
	third_last_year = current_year -  3
	fourth_last_year = current_year - 4
	fifth_last_year = current_year - 5
	
	all_payment_entries_current = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND YEAR(`posting_date`) = '{year}'""".format(customer=customer, year=current_year)
	all_payment_entries_current_1 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND YEAR(`posting_date`) = '{year}'""".format(customer=customer, year=last_year)
	all_payment_entries_current_2 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND YEAR(`posting_date`) = '{year}'""".format(customer=customer, year=second_last_year)
	all_payment_entries_current_3 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND YEAR(`posting_date`) = '{year}'""".format(customer=customer, year=third_last_year)
	all_payment_entries_current_4 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND YEAR(`posting_date`) = '{year}'""".format(customer=customer, year=fourth_last_year)
	all_payment_entries_current_5 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND YEAR(`posting_date`) = '{year}'""".format(customer=customer, year=fifth_last_year)
	
	spende_current = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount' FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=all_payment_entries_current), as_dict=True)
	spende_current_1 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount'  FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=all_payment_entries_current_1), as_dict=True)
	spende_current_2 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount'  FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=all_payment_entries_current_2), as_dict=True)
	spende_current_3 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount'  FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=all_payment_entries_current_3), as_dict=True)
	spende_current_4 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount'  FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=all_payment_entries_current_4), as_dict=True)
	spende_current_5 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount'  FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=all_payment_entries_current_5), as_dict=True)
	
	spenden_aktuelles_jahr = 0
	total = 0
	
	if spende_current[0].amount:
		spenden_aktuelles_jahr += spende_current[0].amount * -1
		total += spende_current[0].amount * -1
	if spende_current_1[0].amount:
		total += spende_current_1[0].amount * -1
	if spende_current_2[0].amount:
		total += spende_current_2[0].amount * -1
	if spende_current_3[0].amount:
		total += spende_current_3[0].amount * -1
	if spende_current_4[0].amount:
		total += spende_current_4[0].amount * -1
	if spende_current_5[0].amount:
		total += spende_current_5[0].amount * -1
		
	return {
			"aktuell": spenden_aktuelles_jahr,
			"total": total
		}