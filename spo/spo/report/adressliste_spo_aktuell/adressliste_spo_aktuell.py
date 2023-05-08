# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from six.moves import range
from six import iteritems
import frappe
from frappe.utils.data import nowdate
from frappe.utils import cint


def execute(filters=None):
    columns, data = get_columns(filters), get_data(filters)
    return columns, data

def get_columns(filters):
    if filters.base_data == "Kunden / Mitglieder":
        return [
            "Kunde:Link/Customer",
            "Kundengruppe::100",
            "Schenkende Rechnung an Dritte:Check",
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
    elif filters.base_data == "Lieferanten":
        return [
            "Lieferant:Link/Supplier",
            "Lieferantengruppe::100",
            "SPO Aktuell",
            "Anrede",
            "Vorname",
            "Nachname",
            "E-Mail",
            "Strasse und Hausnummer",
            "Zusatz",
            "PLZ",
            "Ort",
            "Sprache"
        ]

def get_data(filters):
    data = []
    for customer_or_supplier in get_all_customers_or_suppliers(filters):
        contacts = get_customer_or_supplier_contacts(customer_or_supplier.name)
        if contacts:
            for contact in contacts:
                _data = []
                _data.append(customer_or_supplier.name)
                _data.append(customer_or_supplier.group)
                if filters.base_data == "Kunden / Mitglieder":
                    _data.append(cint(customer_or_supplier.schenkende_rechnung_dritte))
                _data.append(customer_or_supplier.spo_aktuell or '-')
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
                address = get_address(customer_or_supplier.name)
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
                _data.append(customer_or_supplier.language)
                if filters.base_data == "Kunden / Mitglieder":
                    current_mitgliedschaft = get_current_mitgliedschaft(customer_or_supplier.name)
                    _data.append(current_mitgliedschaft)
                    if current_mitgliedschaft != "Keine Mitgliedschaft!":
                        _data.append(get_current_mitgliedschaft_bezahlung(customer_or_supplier.name))
                    else:
                        _data.append(0)
                data.append(_data)
        else:
                _data = []
                _data.append(customer_or_supplier.name)
                _data.append(customer_or_supplier.group)
                if filters.base_data == "Kunden / Mitglieder":
                    _data.append(cint(customer_or_supplier.schenkende_rechnung_dritte))
                _data.append(customer_or_supplier.spo_aktuell or '-')
                _data.append("...")
                _data.append("...")
                _data.append("...")
                _data.append("...")
                address = get_address(customer_or_supplier.name)
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
                _data.append(customer_or_supplier.language)
                if filters.base_data == "Kunden / Mitglieder":
                    current_mitgliedschaft = get_current_mitgliedschaft(customer_or_supplier.name)
                    _data.append(current_mitgliedschaft)
                    if current_mitgliedschaft != "Keine Mitgliedschaft!":
                        _data.append(get_current_mitgliedschaft_bezahlung(customer_or_supplier.name))
                    else:
                        _data.append(0)
                data.append(_data)
    return data

def get_all_customers_or_suppliers(filters):
    if filters.base_data == "Kunden / Mitglieder":
        query = """SELECT `name`, `customer_group` AS `group`, `spo_aktuell`, `language`, `schenkende_rechnung_dritte` FROM `tabCustomer` WHERE `disabled` = 0"""
    elif filters.base_data == "Lieferanten":
        query = """SELECT `name`, `supplier_group` AS `group`, `spo_aktuell`, `language` FROM `tabSupplier` WHERE `disabled` = 0"""
    return frappe.db.sql(query, as_dict=True)

def get_customer_or_supplier_contacts(customer_or_supplier):
    #looking for primary contact
    query = """SELECT `salutation`, `first_name`, `last_name`, `email_id` FROM `tabContact` WHERE `name` IN (SELECT `parent` FROM `tabDynamic Link` WHERE `link_name` = '{customer_or_supplier}' AND `parenttype` = 'Contact')
                AND `is_primary_contact` = 1
                AND `verstorben` = 0""".format(customer_or_supplier=customer_or_supplier)
    contact_list = frappe.db.sql(query, as_dict=True)
    if len(contact_list) < 1:
        #looking for other contact
        query = """SELECT `salutation`, `first_name`, `last_name`, `email_id` FROM `tabContact` WHERE `name` IN (SELECT `parent` FROM `tabDynamic Link` WHERE `link_name` = '{customer_or_supplier}' AND `parenttype` = 'Contact')
                AND `is_primary_contact` = 0
                AND `verstorben` = 0 LIMIT 1""".format(customer_or_supplier=customer_or_supplier)
        contact_list = frappe.db.sql(query, as_dict=True)
        if len(contact_list) < 1:
            return False
        else:
            return contact_list
    else:
        return contact_list

def get_address(customer_or_supplier):
    #looking for primary address
    query = """SELECT `address_line1`, `address_line2`, `plz`, `city` FROM `tabAddress` WHERE `name` IN (SELECT `parent` FROM `tabDynamic Link` WHERE `link_name` = '{customer_or_supplier}' AND `parenttype` = 'Address')
                AND `is_primary_address` = 1 LIMIT 1""".format(customer_or_supplier=customer_or_supplier)
    address = frappe.db.sql(query, as_dict=True)
    if len(address) < 1:
        #looking for other address
        query = """SELECT `address_line1`, `address_line2`, `plz`, `city` FROM `tabAddress` WHERE `name` IN (SELECT `parent` FROM `tabDynamic Link` WHERE `link_name` = '{customer_or_supplier}' AND `parenttype` = 'Address')
                AND `is_primary_address` = 0 LIMIT 1""".format(customer_or_supplier=customer_or_supplier)
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
