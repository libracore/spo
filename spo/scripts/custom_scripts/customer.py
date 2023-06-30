# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import nowdate, add_years, now_datetime
from frappe import _

def default_values_after_insert(self, event):
    if self.customer_type != 'Individual':
        frappe.db.set_value("Customer", self.name, "customer_type", "Individual")
    if self.territory != 'Switzerland':
        frappe.db.set_value("Customer", self.name, "territory", "Switzerland")

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

@frappe.whitelist()
def get_rsv_upload_cred(customer=None, contact=None):
    hash_key = frappe.generate_hash(length=12)
    if customer:
        if frappe.db.exists("Customer", {'rsv_upload_id': hash_key}):
            hash_key = frappe.generate_hash(length=12)
        return {
            'id': hash_key,
            'url': "https://spo.libracore.ch/rsv/upload?id={0}&login=<user-spezifisches-login>".format(hash_key)
        }
    
    if contact:
        # fallback: neu generierung hash falls bereits vorhanden
        if frappe.db.exists("Contact", {'rsv_upload_login': hash_key}):
            hash_key = frappe.generate_hash(length=12)
        
        # suchen nach allen verknüpften Kunden mit upload_id zum generieren aller persönlichen login url's
        url = ''
        contact = frappe.get_doc("Contact", contact)
        for link in contact.links:
            if link.link_doctype == 'Customer':
                customer_upload_id = frappe.db.get_value("Customer", link.link_name, 'rsv_upload_id')
                if customer_upload_id:
                    url += """Kunde: {0}\nLogin URL: https://spo.libracore.ch/rsv/upload?id={1}&login={2}\n\n""".format(link.link_name, customer_upload_id, hash_key)
        return {
            'login': hash_key,
            'url': url
        }
