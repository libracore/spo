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
        {"label": _("Start"), "fieldname": "startdate", "fieldtype": "Time", "width": 160},
        {"label": _("Slot"), "fieldname": "slot", "fieldtype": "Link", "options": "Beratungsslot", "width": 150},
        {"label": _("Thema"), "fieldname": "thema", "fieldtype": "Data", "width": 100},
        {"label": _("Art"), "fieldname": "art", "fieldtype": "Data", "width": 140},
        {"label": _("Berater"), "fieldname": "berater", "fieldtype": "Data", "width": 140},
        {"label": _("Kunde"), "fieldname": "kunde", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Ombudsstellenpartner"), "fieldname": "partner", "fieldtype": "Data", "width": 180},
        {"label": _("Satus"), "fieldname": "status", "fieldtype": "Data", "width": 70},
    ]

def get_data(filters):
    if type(filters) is str:
        filters = ast.literal_eval(filters)
    else:
        filters = dict(filters)
    
    conditions = ""
    if 'from_date' in filters and filters['from_date']:
        conditions += """ AND (`tabBeratungsslot`.`start` >= '{from_date}' OR `tabBeratungsslot`.`start` IS NULL)""".format(from_date=filters['from_date'])
    if 'to_date' in filters and filters['to_date']:
        conditions += """ AND (`tabBeratungsslot`.`start` <= '{to_date}' OR `tabBeratungsslot`.`start` IS NULL)""".format(to_date=filters['to_date'])
    if 'customer' in filters:
        conditions = """ AND `tabBeratungsslot`.`customer` = "{customer}" """.format(customer=filters['customer'])
        
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
        WHERE `tabBeratungsslot`.`status` = "bezahlt" OR `tabBeratungsslot`.`status` = "inklusive"
            {conditions}
        ORDER BY `tabBeratungsslot`.`start` ASC
      """.format(conditions=conditions)
    #frappe.throw(sql_query)
    data = frappe.db.sql(sql_query, as_dict=True)

    return data
