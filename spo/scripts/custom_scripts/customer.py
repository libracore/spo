# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import nowdate, add_years

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