# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import add_days, nowdate

def cleanup_anfragen():
    anfragen = frappe.db.sql("""SELECT `name` FROM `tabAnfrage` WHERE `docstatus` = 0 AND `name` NOT IN (SELECT `spo_referenz` FROM `tabTimesheet Detail` WHERE `spo_dokument` = 'Anfrage')""", as_dict=True)
    for _anfrage in anfragen:
        anfrage = frappe.get_doc("Anfrage", _anfrage.name)
        anfrage.delete()

def cleanup_anonyme_ansichten():
    med_bers = frappe.db.sql("""SELECT `name` FROM `tabMed Ber Anonym`""", as_dict=True)
    for med_ber in med_bers:
        med_ber = frappe.get_doc("Med Ber Anonym", med_ber.name)
        med_ber.delete()

    tragen_anonym = frappe.db.sql("""SELECT `name` FROM `tabTriage Anonym`""", as_dict=True)
    for trage_anonym in tragen_anonym:
        trage_anonym = frappe.get_doc("Triage Anonym", trage_anonym.name)
        trage_anonym.delete()

def cleanup_slots():
    # cancel old unpaid slots
    date = add_days(nowdate(), -10)
    slots = frappe.db.sql("""SELECT `name` FROM `tabBeratungsslot` WHERE `status` = 'reserviert' AND `tabBeratungsslot`.`start` <= '{date}' """.format(date=date), as_dict=True)
    for slot in slots:
        slot = frappe.get_doc("Beratungsslot", slot.name)
        
        # cancel invoice
        invoices = frappe.db.sql("""SELECT `name` FROM `tabSales Invoice` WHERE `docstatus` = 1 AND `beratungsslot` = '{slot}'""".format(slot=slot.name), as_dict=True)
        for sinv in invoices:
            sinv = frappe.get_doc("Sales Invoice", sinv.name)
            sinv.cancel()
        
        # deactivate customer
        customer = frappe.get_doc("Customer", slot.customer)
        customer.disabled = 1
        customer.save()
        
        # set slot status
        slot.status = 'storniert'
        slot.save()
    
    # delete old unused slots
    date = add_days(nowdate(), -7)
    slots = frappe.db.sql("""SELECT `name` FROM `tabBeratungsslot` WHERE `status` = 'frei' AND `tabBeratungsslot`.`start` <= '{date}' """.format(date=date), as_dict=True)
    for slot in slots:
        slot = frappe.get_doc("Beratungsslot", slot.name)
        slot.delete()
