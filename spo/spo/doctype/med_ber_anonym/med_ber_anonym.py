# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MedBerAnonym(Document):
    pass

@frappe.whitelist()
def create_view(med_ber):
    med_ber = frappe.get_doc("Medizinischer Bericht", med_ber)
    anonymer_med_ber = frappe.get_doc({
        "doctype": "Med Ber Anonym",
        "instutition": med_ber.instutition,
        'mandat_angenommen': med_ber.mandat_angenommen,
        'gutachter': med_ber.gutachter,
        'problemstellung': med_ber.problemstellung,
        'diagnose': med_ber.diagnose,
        'operation': med_ber.operation,
        'arzt': med_ber.arzt,
        'verantwortlicher_arzt_sicht_patient': med_ber.verantwortlicher_arzt_sicht_patient,
        'ausgangslage': med_ber.ausgangslage,
        'korrespondenz': med_ber.korrespondenz,
        'bemerkung': med_ber.bemerkung,
        'situation_heute': med_ber.situation_heute,
        'beurteilung': med_ber.beurteilung,
        'fragestellung_anwalt': med_ber.fragestellung_anwalt,
        'fazit': med_ber.fazit,
        'empfehlung': med_ber.empfehlung
    })
    anonymer_med_ber.insert()
    return anonymer_med_ber.name