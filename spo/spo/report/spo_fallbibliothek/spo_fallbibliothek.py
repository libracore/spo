# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns, data = [
        {"label": _("Medizinischer Bericht"), "fieldname": "med_ber", "fieldtype": "Link", "options": "Medizinischer Bericht"},
        {"label": _("Triage"), "fieldname": "triage", "fieldtype": "Link", "options": "Triage"},
        {"label": _("Problemstellung"), "fieldname": "problemstellung", "fieldtype": "Text Editor"},
        {"label": _("Diagnose"), "fieldname": "diagnose", "fieldtype": "Text Editor"},
        {"label": _("Fragestellung"), "fieldname": "fragestellung", "fieldtype": "Text Editor"},
        {"label": _("Berater*in"), "fieldname": "berater_in", "fieldtype": "Data"}
        ], []
    
    med_bers = frappe.db.sql("""SELECT `name`, `problemstellung`, `diagnose`, `owner` FROM `tabMedizinischer Bericht`""", as_dict=True)
    for med_ber in med_bers:
        _data = []
        _data.append(med_ber.name)
        _data.append('---')
        _data.append(med_ber.problemstellung)
        _data.append(med_ber.diagnose)
        _data.append('---')
        _data.append(med_ber.owner)
        data.append(_data)
    
    triagen = frappe.db.sql("""SELECT `name`, `problemstellung`, `fragestellung_anwalt`, `owner` FROM `tabTriage`""", as_dict=True)
    for triage in triagen:
        _data = []
        _data.append('---')
        _data.append(triage.name)
        _data.append(triage.problemstellung)
        _data.append('---')
        _data.append(triage.fragestellung_anwalt)
        _data.append(med_ber.owner)
        data.append(_data)
    
    return columns, data
