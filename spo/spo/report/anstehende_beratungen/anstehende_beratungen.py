# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    return[
        {"label": _("Beratungsslot-Link"), "fieldname": "name", "fieldtype": "Link", "options": "Beratungsslot", "width": 80},
        {"label": _("Start"), "fieldname": "start", "fieldtype": "Datetime", "width": 120},
        {"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 120},
        {"label": _("Customer Link"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 60},
        {"label": _("Thema"), "fieldname": "topic", "fieldtype": "Link", "options": "Beratungsthema", "width": 60},
        {"label": _("Telefon"), "fieldname": "phone", "fieldtype": "Data", "width": 60},
        {"label": _("Email"), "fieldname": "email", "fieldtype": "Data", "width": 80},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Select", "width": 60},
        {"label": _("End"), "fieldname": "end", "fieldtype": "Datetime", "width": 120},
        {"label": _("Berater"), "fieldname": "user", "fieldtype": "Link", "options": "Beraterzuweisung", "width": 120}
    ]


def get_data(filters):
    if not filters.user:
        filters.user = "%"
    
    sql_query = """SELECT 
    `tabBeratungsslot`.`name` AS `name`, 
    `tabBeratungsslot`.`start` AS `start`,
    `tabBeratungsslot`.`customer_name` AS `customer_name`, 
    `tabBeratungsslot`.`customer` AS `customer`, 
    `tabBeratungsslot`.`topic` AS `topic`, 
    `tabBeratungsslot`.`phone` AS `phone`,
    `tabBeratungsslot`.`email` AS `email`, 
    `tabBeratungsslot`.`status` AS `status`,
    `tabBeratungsslot`.`end` AS `end`,
    `tabBeratungsslot`.`user` AS `user`
    FROM 
    `tabBeratungsslot` 
    WHERE 
    `tabBeratungsslot`.`user` = '{user}' 
        AND `tabBeratungsslot`.`start` >= '{start}' 
        AND `tabBeratungsslot`.`end` <= {end}'""".format(user=filters.user, start=filters.start, end=filters.end)
    
    data = frappe.db.sql(sql_query, as_dict=True)
        
    return data
