# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

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