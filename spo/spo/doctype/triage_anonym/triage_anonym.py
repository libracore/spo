# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class TriageAnonym(Document):
    pass

@frappe.whitelist()
def create_view(triage):
    triage = frappe.get_doc("Triage", triage)
    anonyme_triage = frappe.get_doc({
        "doctype": "Triage Anonym",
        "problemstellung": triage.problemstellung,
        "fragestellung_anwalt": triage.fragestellung_anwalt,
        "beurteilung": triage.beurteilung,
        "bemerkung": triage.bemerkung,
        "fazit": triage.fazit,
        "empfehlung": triage.empfehlung
    })
    anonyme_triage.insert()
    return anonyme_triage.name