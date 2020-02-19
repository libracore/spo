# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime, timedelta
from frappe import _

def execute(filters=None):
    columns = get_columns()

    data = get_data(filters.from_date, filters.to_date)

    return columns, data

def get_columns():
    return [
        {"label": _("Beschreibung"), "fieldname": "description", "fieldtype": "Data", "width": 200},
        {"label": _("Konto"), "fieldname": "account", "fieldtype": "Data", "width": 150},
        {"label": _("Betrag"), "fieldname": "amount", "fieldtype": "Data", "width": 150},
        {"label": _("Steuer"), "fieldname": "tax", "fieldtype": "Data", "width": 150}
    ]

def get_data(from_date, to_date):
    data = []
    
    data.append({'description': 'Umsätze', 'account': 'Konto', 'amount': 'Betrag', 'tax': None})
    
    summe_6p1 = 0.0
    # 3110
    sql_query = """SELECT 1.077 * SUM(`credit` - `debit`) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3110%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_6p1 += betrag
    data.append({'description': '6.1%', 'account': '3110', 'amount': betrag, 'tax': None})
    # 3100
    sql_query = """SELECT 1.077 * SUM(`credit` - `debit`) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3100%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_6p1 += betrag
    data.append({'description': '', 'account': '3100', 'amount': betrag, 'tax': None})
    #3120
    sql_query = """SELECT 1.077 * SUM(`credit` - `debit`) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3120%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_6p1 += betrag
    data.append({'description': '', 'account': '3120', 'amount': betrag, 'tax': None})
    # 3130
    sql_query = """SELECT 1.077 * SUM(`credit` - `debit`) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3130%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_6p1 += betrag
    data.append({'description': '', 'account': '3130', 'amount': betrag, 'tax': None})
    # 3140
    sql_query = """SELECT 1.077 * SUM(`credit` - `debit`) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3140%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_6p1 += betrag
    data.append({'description': '', 'account': '3140', 'amount': betrag, 'tax': None}
    # total 6.1%
    tax_6p1 = summe_6p1 * 0.061
    data.append({'description': '', 'account': 'Total', 'amount': summe_6p1, 'tax': tax_6p1}
    # 3241
    summe_3p7 = 0.0
    sql_query = """SELECT 1.077 * SUM(`credit` - `debit`) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3241%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_3p7 += betrag
    data.append({'description': '3.7%', 'account': '3241', 'amount': betrag, 'tax': None}
    # total 3.7%
    tax_3p7 = summe_3p7 * 0.037
    data.append({'description': '', 'account': 'Total', 'amount': summe_3p7, 'tax': tax_3p7}
    # 3210
    summe_2p1 = 0.0
    sql_query = """SELECT 1.025 * SUM(`credit` - `debit`) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3210%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_2p1 += betrag
    data.append({'description': '2.1%', 'account': '3210', 'amount': betrag, 'tax': None}
    # 3215
    sql_query = """SELECT 1.025 * SUM(`credit` - `debit`) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3215%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_2p1 += betrag
    data.append({'description': '', 'account': '3215', 'amount': betrag, 'tax': None}
    # total 2.1%
    tax_2p1 = summe_2p1 * 0.021
    data.append({'description': '', 'account': 'Total', 'amount': summe_2p1, 'tax': tax_2p1}
    # 3200
    summe_0p6 = 0.0
    sql_query = """SELECT 1.025 * SUM(`credit` - `debit`) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3200%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_0p6 += betrag
    data.append({'description': '0.6%', 'account': '3200', 'amount': betrag, 'tax': None}
    # 3202
    sql_query = """SELECT 1.025 * SUM(`credit` - `debit`) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3202%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_0p6 += betrag
    data.append({'description': '0.6%', 'account': '3202', 'amount': betrag, 'tax': None}
    # 3204
    sql_query = """SELECT 1.025 * SUM(`credit` - `debit`) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3204%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_0p6 += betrag
    data.append({'description': '0.6%', 'account': '3204', 'amount': betrag, 'tax': None}
    # 3220
    sql_query = """SELECT 1.025 * SUM(`credit` - `debit`) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3220%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_0p6 += betrag
    data.append({'description': '0.6%', 'account': '3220', 'amount': betrag, 'tax': None}
    # 3230
    sql_query = """SELECT 1.025 * SUM(`credit` - `debit`) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3230%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_0p6 += betrag
    data.append({'description': '0.6%', 'account': '3230', 'amount': betrag, 'tax': None}
    # total 0.6%
    tax_0p6 = summe_0p6 * 0.006
    data.append({'description': '', 'account': 'Total', 'amount': summe_0p6, 'tax': tax_0p6}
    # 3240
    summe_0p1 = 0.0
    sql_query = """SELECT 1.025 * SUM(`credit` - `debit`) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3240%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_0p1 += betrag
    data.append({'description': '0.1%', 'account': '3240', 'amount': betrag, 'tax': None}
    # total 0.1%
    tax_0p1 = summe_0p1 * 0.001
    data.append({'description': '', 'account': 'Total', 'amount': summe_0p1, 'tax': tax_0p1}
    # summe umsätze
    total_summen = summe_6p1 + summe_3p7 + summe_2p1 + summe_0p6 + summe_0p1
    total_steuern = tax_6p1 + tax_3p7 + tax_2p1 + tax_0p6 + tax_0p1
    data.append({'description': 'Summe Umsätzte', 'account': '(Ziffer 299)', 'amount': total_summen, 'tax': total_steuern}
    if total_summen > 0:
        avg_pps = (100 * total_steuern) / total_summen
    else:
        avg_pps = 0
    data.append({'description': 'Durchschnitts-PPS', 'account': '', 'amount': '', 'tax': avg_pps}
    data.append({'description': '', 'account': '', 'amount': '', 'tax': ''}
    # excluded revenue
    data.append({'description': 'Ausgenommene Umsätze', 'account': '', 'amount': '', 'tax': ''}
    excluded = 0.0
    # 6810
    sql_query = """SELECT 1.0 * SUM(`credit` - `debit`) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "6810%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    excluded += betrag
    data.append({'description': '', 'account': '6810', 'amount': betrag, 'tax': None}
    # 6850
    sql_query = """SELECT 1.0 * SUM(`credit` - `debit`) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "6850%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    excluded += betrag
    data.append({'description': '', 'account': '6850', 'amount': betrag, 'tax': None}
    # total asugenommen
    data.append({'description': 'Total', 'account': '(Ziffer 230)', 'amount': excluded, 'tax': None}
    # total Umsatz
    total_200 = excluded + total_summen
    data.append({'description': 'Total Umsatz', 'account': '(Ziffer 200)', 'amount': total_200, 'tax': None}
    # subventionen
    sql_query = """SELECT 1.0 * SUM(`credit` - `debit`) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3010%";""".format(from_date=from_date, to_date=to_date)
    subventionen = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    data.append({'description': 'Subventionen (Ziffer 900)', 'account': '3010', 'amount': subventionen, 'tax': None}
    # spenden, beiträge GöV
    total_spenden = 0.0
    # 3000
    sql_query = """SELECT 1.0 * SUM(`credit` - `debit`) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3000%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    total_spenden += betrag
    data.append({'description': 'Spenden, Beiträge GöV', 'account': '3000', 'amount': betrag, 'tax': None}
    # 3020
    sql_query = """SELECT 1.0 * SUM(`credit` - `debit`) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3020%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    total_spenden += betrag
    data.append({'description': '', 'account': '3020', 'amount': betrag, 'tax': None}
    # 3030
    sql_query = """SELECT 1.0 * SUM(`credit` - `debit`) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3030%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    total_spenden += betrag
    data.append({'description': '', 'account': '3030', 'amount': betrag, 'tax': None}
    # 3040
    sql_query = """SELECT 1.0 * SUM(`credit` - `debit`) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3040%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    total_spenden += betrag
    data.append({'description': '', 'account': '3040', 'amount': betrag, 'tax': None}
    # total spenden
    data.append({'description': 'Total Spenden', 'account': '(Ziffer 910)', 'amount': total_spenden, 'tax': None}
    # gesamtumsatz
    data.append({'description': '', 'account': '', 'amount': '', 'tax': ''}
    data.append({'description': 'Gesamtumsatz', 'account': '', 'amount': total_200 + subventionen + total_spenden, 'tax': ''}
    
    return data
