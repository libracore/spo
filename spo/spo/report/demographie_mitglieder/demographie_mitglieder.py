# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Mitglied"), "fieldname": "mitglied", "fieldtype": "Link", "options": "Customer"},
        {"label": _("Mitgliedschaft"), "fieldname": "mitgliedschaft", "fieldtype": "Link", "options": "Mitgliedschaft"},
        {"label": _("Typ"), "fieldname": "mitgliedschafts_typ", "fieldtype": "Select", "options": "Einzelmitglied\nFamilienmitglied\nPassiv-/Kollektivmitglied\nFreimitglied"},
        {"label": _("Mitgliedschafts Ende"), "fieldname": "enddatum", "fieldtype": "Date"},
        {"label": _("Anz. Mitgliedschaften"), "fieldname": "qty", "fieldtype": "Int"},
        {"label": _("Geschlecht"), "fieldname": "geschlecht", "fieldtype": "Link", "options": "Gender"},
        {"label": _("Anrede"), "fieldname": "anrede", "fieldtype": "Link", "options": "Salutation"},
        {"label": _("Vorname"), "fieldname": "vorname", "fieldtype": "Data"},
        {"label": _("Nachname"), "fieldname": "nachname", "fieldtype": "Data"},
        {"label": _("Geburtsdatum"), "fieldname": "geburtsdatum", "fieldtype": "Date"},
        {"label": _("Strasse"), "fieldname": "strasse", "fieldtype": "Data"},
        {"label": _("PLZ"), "fieldname": "plz", "fieldtype": "Int"},
        {"label": _("Ort"), "fieldname": "ort", "fieldtype": "Data"},
        {"label": _("Kanton"), "fieldname": "kanton", "fieldtype": "Data"},
        {"label": _("Saldo"), "fieldname": "saldo", "fieldtype": "Currency"}
    ]

def get_data(filters):
    query = """
        SELECT DISTINCT
            `a`.`mitglied`,
            `a`.`mitgliedschaft`,
            `a`.`mitgliedschafts_typ`,
            `a`.`enddatum`,
            `d`.`qty`,
            `b`.`geschlecht`,
            `b`.`anrede`,
            `b`.`vorname`,
            `b`.`nachname`,
            `b`.`geburtsdatum`,
            `a`.`strasse`,
            `a`.`plz`,
            `a`.`ort`,
            `a`.`kanton`,
            `c`.`saldo`
        FROM (
            SELECT
                `ms`.`mitglied` AS `mitglied`,
                `ms`.`name` AS `mitgliedschaft`,
                `ms`.`mitgliedschafts_typ` AS `mitgliedschafts_typ`,
                `ms`.`ende` AS `enddatum`,
                `addr`.`address_line1` AS `strasse`,
                `addr`.`plz` AS `plz`,
                `addr`.`city` AS `ort`,
                `addr`.`kanton` AS `kanton`,
                `dynlink`.`parenttype`
            FROM `tabMitgliedschaft` AS `ms`
            JOIN `tabDynamic Link` AS `dynlink` ON `ms`.`mitglied` = `dynlink`.`link_name`
            JOIN `tabAddress` AS `addr` ON `dynlink`.`parent` = `addr`.`name`
        ) AS `a`
        JOIN (
            SELECT
                `ms`.`mitglied` AS `mitglied`,
                `con`.`first_name` AS `vorname`,
                `con`.`last_name` AS `nachname`,
                `con`.`salutation` AS `anrede`,
                `con`.`gender` AS `geschlecht`,
                `con`.`geburtsdatum` AS `geburtsdatum`
            FROM `tabMitgliedschaft` AS `ms`
            JOIN `tabDynamic Link` AS `dynlink` ON `ms`.`mitglied` = `dynlink`.`link_name`
            JOIN `tabContact` AS `con` ON `dynlink`.`parent` = `con`.`name`
        ) AS `b` ON `a`.`mitglied` = `b`.`mitglied`
        JOIN (
            SELECT 
                `tabGL Entry`.`party`,
                ((SUM(`tabGL Entry`.`debit_in_account_currency`) - SUM(`tabGL Entry`.`credit_in_account_currency`)) * -1) AS `saldo`
            FROM `tabGL Entry`
            WHERE `tabGL Entry`.`party_type` = 'Customer'
            GROUP BY `tabGL Entry`.`party`
        ) AS `c` ON `a`.`mitglied` = `c`.`party`
        JOIN (
            SELECT 
                COUNT(`name`) AS `qty`,
                `mitglied`
            FROM `tabMitgliedschaft`
            GROUP BY `mitglied`
        ) AS `d` ON `a`.`mitglied` = `d`.`mitglied`
        WHERE `a`.`enddatum` >= CURDATE()
    """
    
    return frappe.db.sql(query, as_dict=True)
