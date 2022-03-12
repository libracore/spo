# Copyright (c) 2016-2022, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils.data import getdate

def execute(filters=None):
    # prepare columns
    columns = [
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
    ]
    
    # prepare data
    data = []
        
    # loop through mandates
    mandate = frappe.db.sql("""SELECT `name` FROM `tabMandat`""", as_dict=True)
    for mandat in mandate:
        row = {
            'mandat': mandat['name'],
            'pinv_name': None,
            'pinv': 0.00,
            'pinv_date': None,
            'sinv_name': None,
            'sinv': 0.00,
            'sinv_date': None,
            'saldo': 0.00
        }
        pinv_amount = 0
        sinv_amount = 0
        # get purchase invoices
        pinv = frappe.db.sql("""
            SELECT 
                `grand_total`, `posting_date`, `name` FROM `tabPurchase Invoice` 
            WHERE 
                `mandat` = '{mandat}' 
                AND `docstatus` != '2' 
                AND `posting_date` >= '{abgleich_ab}' 
                AND `posting_date` <= '{abgleich_bis}'
            LIMIT 1""".format(mandat=mandat[0], abgleich_ab=filters.abgleich_ab, abgleich_bis=filters.abgleich_bis), 
            as_dict=True)
        if len(pinv) > 0:
            row['pinv_name'] = pinv[0]['name']
            row['pinv'] = pinv[0]['grand_total']
            row['pinv_date'] = pinv[0]['posting_date']
            if pinv[0]['grand_total']:
                pinv_amount = float(pinv[0]['grand_total'])
        # get sales invoices
        sinv = frappe.db.sql("""
            SELECT 
                `tabSales Invoice`.`name`, 
                `tabSales Invoice`.`posting_date`, 
                `tabSales Invoice`.`status`,
                SUM(`tabSales Invoice Item`.`amount`) AS `amount`,
                `tabPayment Entry Reference`.`modified`
            FROM `tabSales Invoice Item` 
            LEFT JOIN `tabSales Invoice` ON `tabSales Invoice`.`name` = `tabSales Invoice Item`.`parent`
            LEFT JOIN `tabPayment Entry Reference` ON (
                `tabPayment Entry Reference`.`parentfield` = 'references' 
                AND `tabPayment Entry Reference`.`parenttype` = 'Payment Entry' 
                AND `tabPayment Entry Reference`.`reference_name` = `tabSales Invoice`.`name`
                AND `tabPayment Entry Reference`.`docstatus` = 1)
            WHERE 
                `tabSales Invoice`.`mandat` = '{mandat}' 
                AND `tabSales Invoice`.`docstatus` != '2' 
                AND `tabSales Invoice`.`posting_date` >= '{abgleich_ab}'
                AND `tabSales Invoice`.`posting_date` <= '{abgleich_bis}'
                AND `tabSales Invoice Item`.`item_code` = 'Mandatsverrechnung (exkl. MwSt)'
            GROUP BY `tabSales Invoice`.`name`
                """.format(mandat=mandat[0], abgleich_ab=filters.abgleich_ab, abgleich_bis=filters.abgleich_bis),
            as_dict=True)
        if len(sinv) > 0:
            row['sinv_name'] = sinv[0]['name']
            if sinv[0]['amount']:
                sinv_amount = float(sinv[0]['amount'])
                row['sinv'] = sinv_amount
            row['sinv_date'] = sinv[0]['posting_date']
            row['rechnungsstatus'] = sinv[0]['status']
            row['payment_date'] = sinv[0]['modified']

        saldo = 0 - pinv_amount + sinv_amount
        row['saldo'] = saldo
        if filters.nur_offene == 0 or (filters.nur_offene == 1 and saldo != 0):
            data.append(row)
        
    return columns, data
