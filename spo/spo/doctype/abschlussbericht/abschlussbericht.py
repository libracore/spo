# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import formatdate

class Abschlussbericht(Document):
    pass

@frappe.whitelist()
def get_titelzeile(kontakt, adresse, referenz):
    kontakt = frappe.get_doc("Contact", kontakt)
    adresse = frappe.get_doc("Address", adresse)
    titelzeile = '<b>Abschlussbericht SPO<br>Ihre Referenz: '
    if referenz:
        titelzeile += referenz
    titelzeile += '<br>'
    if kontakt.verstorben == 1:
        if kontakt.salutation:
            titelzeile += kontakt.salutation + " "
        titelzeile += kontakt.first_name + " "
        titelzeile += kontakt.last_name + " (verstorben"
        if kontakt.verstorben_am:
            titelzeile += " am " + formatdate(kontakt.verstorben_am) + "), "
        else:
            titelzeile += "), "
        if kontakt.geburtsdatum:
            titelzeile += "geboren am " + formatdate(kontakt.geburtsdatum) + ", "
        titelzeile += adresse.address_line1 + " "
        titelzeile += adresse.plz + " "
        titelzeile += adresse.city + "</b>"
        return titelzeile
    else:
        if kontakt.salutation:
            titelzeile += kontakt.salutation + " "
        titelzeile += kontakt.first_name + " "
        titelzeile += kontakt.last_name + ", "
        if kontakt.geburtsdatum:
            titelzeile += "geboren am " + formatdate(kontakt.geburtsdatum) + ", "
        titelzeile += adresse.address_line1 + " "
        titelzeile += adresse.plz + " "
        titelzeile += adresse.city + "</b>"
        return titelzeile
