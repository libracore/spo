# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from six.moves import range
from six import iteritems
import frappe
from frappe.utils.data import nowdate


def execute(filters=None):
    columns, data = get_columns(filters), get_data(filters)
    return columns, data

def get_columns(filters):
    return [
        "Kunde:Link/Customer",
        "Kundengruppe::100",
        "SPO Aktuell",
        "Anrede",
        "Vorname",
        "Nachname",
        "E-Mail",
        "Strasse und Hausnummer",
        "Zusatz",
        "PLZ",
        "Ort",
        "Sprache",
        "Mitgliedschaft",
        "Unbezahlt:Check"
    ]

def get_data(filters):
    data = []
    for customer in get_all_customers(filters):
        _data = []
        _data.append(customer.name)
        _data.append(customer.customer_group)
        _data.append(customer.spo_aktuell)
        contact = get_contact(customer.name)
        if contact:
            _data.append(contact.salutation)
            _data.append(contact.first_name)
            _data.append(contact.last_name)
            _data.append(contact.email_id)
        else:
            _data.append("...")
            _data.append("...")
            _data.append("...")
            _data.append("...")
        address = get_address(customer.name)
        if address:
            _data.append(address.address_line1)
            _data.append(address.address_line2)
            _data.append(address.plz)
            _data.append(address.city)
        else:
            _data.append("...")
            _data.append("...")
            _data.append("...")
            _data.append("...")
        _data.append(customer.language)
        current_mitgliedschaft = get_current_mitgliedschaft(customer.name)
        _data.append(current_mitgliedschaft)
        if current_mitgliedschaft != "Keine Mitgliedschaft!":
            _data.append(get_current_mitgliedschaft_bezahlung(customer.name))
        else:
            _data.append(0)
        data.append(_data)
    return data

def get_all_customers(filters):
    query = """SELECT `name`, `customer_group`, `spo_aktuell`, `language` FROM `tabCustomer` WHERE `disabled` = 0"""
    if not filters.customer_group:
        query += """ AND (`customer_group` IN ('Mitglied', 'Newsletter Abo') OR `schenkende_rechnung_dritte` = 1)"""
    elif filters.customer_group == 'Schenkende Rechnung an Dritte':
        query += """ AND `customer_group` NOT IN ('Mitglied', 'Newsletter Abo') AND `schenkende_rechnung_dritte` = 1"""
    else:
        query += """ AND `customer_group` = '{customer_group}'""".format(customer_group=filters.customer_group)
    return frappe.db.sql(query, as_dict=True)

def get_contact(customer):
    #looking for primary contact
    query = """SELECT `salutation`, `first_name`, `last_name`, `email_id` FROM `tabContact` WHERE `name` IN (SELECT `parent` FROM `tabDynamic Link` WHERE `link_name` = '{customer}' AND `parenttype` = 'Contact')
                AND `is_primary_contact` = 1
                AND `verstorben` = 0 LIMIT 1""".format(customer=customer)
    contact = frappe.db.sql(query, as_dict=True)
    if len(contact) < 1:
        #looking for other contact
        query = """SELECT `salutation`, `first_name`, `last_name`, `email_id` FROM `tabContact` WHERE `name` IN (SELECT `parent` FROM `tabDynamic Link` WHERE `link_name` = '{customer}' AND `parenttype` = 'Contact')
                AND `is_primary_contact` = 0
                AND `verstorben` = 0 LIMIT 1""".format(customer=customer)
        contact = frappe.db.sql(query, as_dict=True)
        if len(contact) < 1:
            return False
        else:
            return contact[0]
    else:
        return contact[0]

def get_address(customer):
    #looking for primary address
    query = """SELECT `address_line1`, `address_line2`, `plz`, `city` FROM `tabAddress` WHERE `name` IN (SELECT `parent` FROM `tabDynamic Link` WHERE `link_name` = '{customer}' AND `parenttype` = 'Address')
                AND `is_primary_address` = 1 LIMIT 1""".format(customer=customer)
    address = frappe.db.sql(query, as_dict=True)
    if len(address) < 1:
        #looking for other address
        query = """SELECT `address_line1`, `address_line2`, `plz`, `city` FROM `tabAddress` WHERE `name` IN (SELECT `parent` FROM `tabDynamic Link` WHERE `link_name` = '{customer}' AND `parenttype` = 'Address')
                AND `is_primary_address` = 0 LIMIT 1""".format(customer=customer)
        address = frappe.db.sql(query, as_dict=True)
        if len(address) < 1:
            return False
        else:
            return address[0]
    else:
        return address[0]

def get_current_mitgliedschaft(customer):
    query = """SELECT `start`, `ende` FROM `tabMitgliedschaft` WHERE `mitglied` = '{customer}' ORDER BY `ende` DESC LIMIT 1""".format(customer=customer)
    mitgliedschaft = frappe.db.sql(query, as_dict=True)
    if len(mitgliedschaft) == 1:
        return str(mitgliedschaft[0].start) + " - " + str(mitgliedschaft[0].ende)
    else:
        return "Keine Mitgliedschaft!"

def get_current_mitgliedschaft_bezahlung(customer):
    query = """SELECT `rechnung` FROM `tabMitgliedschaft` WHERE `mitglied` = '{customer}' ORDER BY `ende` DESC LIMIT 1""".format(customer=customer)
    sinv = frappe.db.sql(query, as_dict=True)
    if len(sinv) == 1:
        sinv_status = frappe.db.get_value("Sales Invoice", sinv[0].rechnung, "status")
        if sinv_status != 'Paid':
            return 1
        else:
            return 0
    else:
        return 0
