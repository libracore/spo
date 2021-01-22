# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns, data = [
        {"label": _("Mandat"), "fieldname": "mandat", "fieldtype": "Link", "options": "Mandat"},
        {"label": _("Eingangsrechnung (in CHF)"), "fieldname": "pinv", "fieldtype": "Float"},
        {"label": _("Datum"), "fieldname": "pinv_date", "fieldtype": "Date", "width": "100"},
        {"label": _("Ausgangsrechnung (in CHF)"), "fieldname": "sinv", "fieldtype": "Float"},
        {"label": _("Datum"), "fieldname": "sinv_date", "fieldtype": "Date", "width": "100"},
        {"label": _("Saldo (in CHF)"), "fieldname": "saldo", "fieldtype": "Float"}
    ], []
    
    mandate = frappe.db.sql("""SELECT `name` FROM `tabMandat`""", as_list=True)
    for mandat in mandate:
        _data = []
        _data.append(mandat[0])
        pinv_amount = 0
        sinv_amount = 0
        pinv = frappe.db.sql("""SELECT `grand_total`, `posting_date` FROM `tabPurchase Invoice` WHERE `mandat` = '{mandat}' AND `docstatus` != '2' LIMIT 1""".format(mandat=mandat[0]), as_dict=True)
        if len(pinv) > 0:
            _data.append(pinv[0].grand_total)
            _data.append(pinv[0].posting_date)
            if pinv[0].grand_total:
                pinv_amount = float(pinv[0].grand_total)
        else:
            _data.append(0.00)
            _data.append("")
        sinv_query = """SELECT `name` FROM `tabSales Invoice` WHERE `mandat` = '{mandat}' AND `docstatus` != '2'""".format(mandat=mandat[0])
        sinv_date = frappe.db.sql("""SELECT `posting_date` FROM `tabSales Invoice` WHERE `mandat` = '{mandat}' AND `docstatus` != '2' LIMIT 1""".format(mandat=mandat[0]), as_list=True)
        if len(sinv_date) > 0:
            sinv = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `parent` IN ({sinv_query}) AND `item_code` = 'Mandatsverrechnung (exkl. MwSt)'""".format(sinv_query=sinv_query), as_list=True)
            if sinv[0][0]:
                sinv_amount = float(sinv[0][0])
                _data.append(sinv[0][0])
            else:
                _data.append(0.00)
            _data.append(sinv_date[0][0])
        else:
            _data.append(0.00)
            _data.append("")
        saldo = 0 - pinv_amount + sinv_amount
        _data.append(saldo)
        data.append(_data)
        
    return columns, data