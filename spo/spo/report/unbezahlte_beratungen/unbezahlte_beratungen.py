# Copyright (c) 2022, libracore and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
import frappe
from frappe import _
import ast
from frappe.utils.data import add_days, nowdate

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Start"), "fieldname": "startdate", "fieldtype": "datetime", "width": 160},
        {"label": _("Slot"), "fieldname": "slot", "fieldtype": "Link", "options": "Beratungsslot", "width": 150},
        {"label": _("Thema"), "fieldname": "thema", "fieldtype": "Data", "width": 100},
        {"label": _("Art"), "fieldname": "art", "fieldtype": "Data", "width": 140},
        {"label": _("Berater"), "fieldname": "berater", "fieldtype": "Data", "width": 140},
        {"label": _("Kunde"), "fieldname": "kunde", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Ombudsstellenpartner"), "fieldname": "partner", "fieldtype": "Link", "options": "Ombudsstellen Partner", "width": 180},
        {"label": _("Satus"), "fieldname": "status", "fieldtype": "Data", "width": 70},
    ]

def get_data(filters):
    from_date = add_days(nowdate(), -7)
        
    # prepare query
    sql_query = """
        SELECT
            `tabBeratungsslot`.`start` AS `startdate`,
            `tabBeratungsslot`.`name` AS `slot`,
            `tabBeratungsslot`.`topic` AS `thema`,
            `tabBeratungsslot`.`consultation_type` AS `art`,
            `tabBeratungsslot`.`user` AS `berater`,
            `tabBeratungsslot`.`customer` AS `kunde`,
            `tabBeratungsslot`.`ombudsstelle` AS `partner`,
            `tabBeratungsslot`.`status` AS `status`,
            `anf`.`customer`
        FROM `tabBeratungsslot`
        JOIN `tabAnfrage` AS `anf` ON `tabBeratungsslot`.`customer` = `anf`.`customer`
        WHERE `tabBeratungsslot`.`status` = "reserviert"
        AND `tabBeratungsslot`.`start` <= '{from_date}'
        ORDER BY `tabBeratungsslot`.`start` ASC
      """.format(from_date=from_date)
    
    data = frappe.db.sql(sql_query, as_dict=True)

    return data
