# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils.data import getdate

def execute(filters=None):
    columns, data = [
        {"label": _("Mandat"), "fieldname": "mandat", "fieldtype": "Link", "options": "Mandat"},
        {"label": _("PINV"), "fieldname": "pinv_name", "fieldtype": "Link", "options": "Purchase Invoice"},
        {"label": _("Eingangsrechnung (in CHF)"), "fieldname": "pinv", "fieldtype": "Float"},
        {"label": _("Datum"), "fieldname": "pinv_date", "fieldtype": "Date", "width": "100"},
        {"label": _("SINV"), "fieldname": "sinv_name", "fieldtype": "Link", "options": "Sales Invoice"},
        {"label": _("Ausgangsrechnung (in CHF)"), "fieldname": "sinv", "fieldtype": "Float"},
        {"label": _("Datum"), "fieldname": "sinv_date", "fieldtype": "Date", "width": "100"},
        {"label": _("Rechnungsstatus"), "fieldname": "rechnungsstatus", "fieldtype": "Data", "width": "100"},
        {"label": _("Datum der Zahlung"), "fieldname": "payment_date", "fieldtype": "Date", "width": "100"},
        {"label": _("Saldo (in CHF)"), "fieldname": "saldo", "fieldtype": "Float"}
    ], []
    
    abgleich_ab = filters.abgleich_ab
    
    mandate = frappe.db.sql("""SELECT `name` FROM `tabMandat`""", as_list=True)
    for mandat in mandate:
        _data = []
        _data.append(mandat[0])
        pinv_amount = 0
        sinv_amount = 0
        pinv = frappe.db.sql("""SELECT `grand_total`, `posting_date`, `name` FROM `tabPurchase Invoice` WHERE `mandat` = '{mandat}' AND `docstatus` != '2' AND `posting_date` >= '{abgleich_ab}' LIMIT 1""".format(mandat=mandat[0], abgleich_ab=abgleich_ab), as_dict=True)
        if len(pinv) > 0:
            _data.append(pinv[0].name)
            _data.append(pinv[0].grand_total)
            _data.append(pinv[0].posting_date)
            if pinv[0].grand_total:
                pinv_amount = float(pinv[0].grand_total)
        else:
            _data.append("")
            _data.append(0.00)
            _data.append("")
        sinv_query = """SELECT `name` FROM `tabSales Invoice` WHERE `mandat` = '{mandat}' AND `docstatus` != '2' AND `posting_date` >= '{abgleich_ab}'""".format(mandat=mandat[0], abgleich_ab=abgleich_ab)
        sinv_date = frappe.db.sql("""SELECT `posting_date`, `status`, `name` FROM `tabSales Invoice` WHERE `mandat` = '{mandat}' AND `docstatus` != '2' AND `posting_date` >= '{abgleich_ab}' LIMIT 1""".format(mandat=mandat[0], abgleich_ab=abgleich_ab), as_dict=True)
        if len(sinv_date) > 0:
            _data.append(sinv_date[0].name)
            sinv = frappe.db.sql("""SELECT SUM(`amount`) FROM `tabSales Invoice Item` WHERE `parent` IN ({sinv_query}) AND `item_code` = 'Mandatsverrechnung (exkl. MwSt)'""".format(sinv_query=sinv_query), as_list=True)
            if sinv[0][0]:
                sinv_amount = float(sinv[0][0])
                _data.append(sinv[0][0])
            else:
                _data.append(0.00)
            _data.append(sinv_date[0].posting_date)
            _data.append(sinv_date[0].status)
            if sinv_date[0].status == 'Paid':
                payment_date = frappe.db.sql("""SELECT `modified` FROM `tabPayment Entry Reference` WHERE `parentfield` = 'references' AND `parenttype` = 'Payment Entry' AND `reference_name` IN ({sinv_query}) LIMIT 1""".format(sinv_query=sinv_query), as_list=True)
                if len(payment_date) > 0:
                    _data.append(getdate(payment_date[0][0]))
                else:
                    _data.append("")
            else:
                _data.append("")
        else:
            _data.append("")
            _data.append(0.00)
            _data.append("")
            _data.append("")
            _data.append("")
        saldo = 0 - pinv_amount + sinv_amount
        _data.append(saldo)
        data.append(_data)
        
    return columns, data
