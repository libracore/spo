# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns, data = [
        {"label": _("Mitarbeiter"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee"},
        {"label": _("Name"), "fieldname": "employee_name", "fieldtype": "Data"},
        {"label": _("Arbeitszeit"), "fieldname": "arbeitszeit", "fieldtype": "Float"},
        {"label": _("Verrechenbar"), "fieldname": "verrechenbar", "fieldtype": "Float"},
        {"label": _("Verrechnet"), "fieldname": "verrechnet", "fieldtype": "Float"},
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
        if _arbeitszeit[0][0]:
            arbeitszeit = _arbeitszeit[0][0]
        else:
            arbeitszeit = 0.00
        _data.append(arbeitszeit)
        
        _verrechenbar = frappe.db.sql("""SELECT SUM(`hours`) FROM `tabTimesheet Detail` WHERE `parent` IN ({timesheets_query}) AND `activity_type` IN ('Beratung', 'Mandatsarbeit')""".format(timesheets_query=timesheets_query), as_list=True)
        if _verrechenbar[0][0]:
            verrechenbar = _verrechenbar[0][0]
        else:
            verrechenbar = 0.00
        _data.append(verrechenbar)
        
        sinv_query = """SELECT `name` FROM `tabSales Invoice` WHERE `docstatus` != '2' AND `company` = 'SPO Schweizerische Patientenorganisation' AND `posting_date` BETWEEN '{start}' AND '{ende}'""".format(start=start, ende=ende)
        _verrechnet = frappe.db.sql("""SELECT SUM(`qty`) FROM `tabSales Invoice Item` WHERE `parent` IN ({sinv_query}) AND `employee` = '{employee}'""".format(sinv_query=sinv_query, employee=employee.name), as_list=True)
        if _verrechnet[0][0]:
            verrechnet = _verrechnet[0][0]
        else:
            verrechnet = 0.00
        _data.append(verrechnet)
        
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
