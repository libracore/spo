# Copyright (c) 2022, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import ast

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
    from_date = frappe.utils.nowdate()
    to_date = frappe.utils.add_months(frappe.utils.nowdate(), 1)
        
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
            `tabBeratungsslot`.`status` AS `status`
        FROM `tabBeratungsslot`
        WHERE`tabBeratungsslot`.`status` IN ("bezahlt", "inklusive")
            AND (`tabBeratungsslot`.`start` >= '{from_date}' OR `tabBeratungsslot`.`start` IS NULL)
            AND (`tabBeratungsslot`.`start` <= '{to_date}' OR `tabBeratungsslot`.`start` IS NULL)
        ORDER BY `tabBeratungsslot`.`start` ASC
      """.format(to_date=to_date, from_date=from_date)
    #frappe.throw(sql_query)
    data = frappe.db.sql(sql_query, as_dict=True)

    return data
