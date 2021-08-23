# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns, data = [
        {"label": _("Mitarbeiter"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee"},
        {"label": _("Name"), "fieldname": "employee_name", "fieldtype": "Data"},
        {"label": _("Summe Arbeitszeit"), "fieldname": "arbeitszeit", "fieldtype": "Float"},
        {"label": _("Verrechenbar"), "fieldname": "verrechenbar", "fieldtype": "Float"},
        {"label": _("Markiert als NV"), "fieldname": "markiert_als_nv", "fieldtype": "Float"},
        {"label": _("NV in %"), "fieldname": "nv_in_prozent", "fieldtype": "Data"},
        {"label": _("Verrechnet"), "fieldname": "verrechnet", "fieldtype": "Float"},
        {"label": _("Verrechnet via Mitgliedschaft"), "fieldname": "verrechnet_via_mitgliedschaft", "fieldtype": "Float"},
        {"label": _("Differenz Kontrolle"), "fieldname": "differenz_kontrolle", "fieldtype": "Float"},
        {"label": _("Differenz Kontrolle in %"), "fieldname": "differenz_kontrolle_in_prozent", "fieldtype": "Data"},
        {"label": _("DB Total in %"), "fieldname": "db_total", "fieldtype": "Data"},
        {"label": _("DB Verrechenbar in %"), "fieldname": "db_verrechenbar", "fieldtype": "Data"}
        ], []
    
    start = filters.from_date
    ende = filters.to_date
    employees = frappe.db.sql("""SELECT `name`, `employee_name` FROM `tabEmployee` WHERE `status` = 'Active'""", as_dict=True)
    for employee in employees:
        _data = []
        _data.append(employee.name)
        _data.append(employee.employee_name)
        
        timesheets_query = """SELECT `name` FROM `tabTimesheet` WHERE `employee` = '{employee}' AND `docstatus` != '2' AND `start_date` BETWEEN '{start}' AND '{ende}'""".format(employee=employee.name, start=start, ende=ende)
        _arbeitszeit = frappe.db.sql("""SELECT SUM(`hours`) FROM `tabTimesheet Detail` WHERE `parent` IN ({timesheets_query}) AND `activity_type` = 'Arbeitszeit'""".format(timesheets_query=timesheets_query), as_list=True)
        pausenzeit = frappe.db.sql("""SELECT SUM(`hours`) FROM `tabTimesheet Detail` WHERE `parent` IN ({timesheets_query}) AND `activity_type` = 'Pause'""".format(timesheets_query=timesheets_query), as_list=True)
        if _arbeitszeit[0][0]:
            if pausenzeit[0][0]:
                arbeitszeit = float(_arbeitszeit[0][0]) - float(pausenzeit[0][0])
            else:
                arbeitszeit = float(_arbeitszeit[0][0])
        else:
            arbeitszeit = 0.00
        _data.append(arbeitszeit)
        
        _verrechenbar = frappe.db.sql("""SELECT SUM(`hours`) FROM `tabTimesheet Detail` WHERE `parent` IN ({timesheets_query}) AND `activity_type` IN ('Beratung', 'Mandatsarbeit')""".format(timesheets_query=timesheets_query), as_list=True)
        if _verrechenbar[0][0]:
            verrechenbar = _verrechenbar[0][0]
        else:
            verrechenbar = 0.00
        _data.append(verrechenbar)
        
        _markiert_als_nv = frappe.db.sql("""SELECT SUM(`hours`) FROM `tabTimesheet Detail` WHERE `parent` IN ({timesheets_query}) AND `activity_type` IN ('Beratung', 'Mandatsarbeit') AND `nicht_verrechnen` = 1""".format(timesheets_query=timesheets_query), as_list=True)
        if _markiert_als_nv[0][0]:
            markiert_als_nv = _markiert_als_nv[0][0]
        else:
            markiert_als_nv = 0.00
        _data.append(markiert_als_nv)
        
        nv_in_prozent = 0.00
        if verrechenbar > 0:
            nv_in_prozent = (100 / verrechenbar) * markiert_als_nv
        _data.append(round(nv_in_prozent, 2))
        
        # nicht verrechnete zeiten aus anfragen ohne mandat aber it mitgliedschaft
        anf_ausschluss_query = """SELECT `anfragen` FROM `tabMandat`"""
        anf_query = """SELECT `name` FROM `tabAnfrage` WHERE `mitgliedschaft` IS NOT NULL AND `name` NOT IN ({anf_ausschluss_query})""".format(anf_ausschluss_query=anf_ausschluss_query)
        _verrechnet_zusatz = frappe.db.sql("""SELECT SUM(`hours`) FROM `tabTimesheet Detail` WHERE `parent` IN ({timesheets_query}) AND `activity_type` = 'Beratung' AND `spo_referenz` IN ({anf_query})""".format(timesheets_query=timesheets_query, anf_query=anf_query), as_list=True)
        if _verrechnet_zusatz[0][0]:
            verrechnet_zusatz = _verrechnet_zusatz[0][0]
        else:
            verrechnet_zusatz = 0.00
        
        sinv_query = """SELECT `name` FROM `tabSales Invoice` WHERE `docstatus` != '2' AND `company` = 'SPO Schweizerische Patientenorganisation' AND `posting_date` BETWEEN '{start}' AND '{ende}'""".format(start=start, ende=ende)
        _verrechnet = frappe.db.sql("""SELECT SUM(`qty`) FROM `tabSales Invoice Item` WHERE `parent` IN ({sinv_query}) AND `employee` = '{employee}'""".format(sinv_query=sinv_query, employee=employee.name), as_list=True)
        if _verrechnet[0][0]:
            verrechnet = _verrechnet[0][0] + verrechnet_zusatz
        else:
            verrechnet = 0.00 + verrechnet_zusatz
        _data.append(verrechnet)
        _data.append(verrechnet_zusatz)
        
        differenz_kontrolle = verrechenbar - verrechnet - markiert_als_nv
        _data.append(differenz_kontrolle)
        differenz_kontrolle_in_prozent = 0.00
        if verrechenbar > 0:
            differenz_kontrolle_in_prozent = (100 / verrechenbar) * differenz_kontrolle
        _data.append(round(differenz_kontrolle_in_prozent, 2))
        
        if arbeitszeit > 0:
            db_total = (100 / arbeitszeit) * verrechnet
            _data.append(round(db_total, 2))
        else:
            if verrechnet > 0:
                db_total = '> 100%'
                _data.append(db_total)
            else:
                db_total = 0.00
                _data.append(round(db_total, 2))
        
        if verrechenbar > 0:
            db_verrechenbar = (100 / verrechenbar) * verrechnet
            _data.append(round(db_verrechenbar, 2))
        else:
            if verrechnet > 0:
                db_verrechenbar = '> 100%'
                _data.append(db_verrechenbar)
            else:
                db_verrechenbar = 0.00
                _data.append(round(db_verrechenbar, 2))
        
        data.append(_data)
    return columns, data
