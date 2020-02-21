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
    
    data.append({'description': '<b>Umsätze</b>', 'account': '<b>Konto</b>', 'amount': '<b>Betrag</b>', 'tax': '<b>Steuer</b>'})
    
    summe_6p1 = 0.0
    # 3110
    sql_query = """SELECT 1.077 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3110%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_6p1 += betrag
    data.append({'description': '6.1%', 'account': '3110', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': ''})
    # 3100
    sql_query = """SELECT 1.077 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3100%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_6p1 += betrag
    data.append({'description': '', 'account': '3100', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': ''})
    #3120
    sql_query = """SELECT 1.077 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3120%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_6p1 += betrag
    data.append({'description': '', 'account': '3120', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': ''})
    # 3130
    sql_query = """SELECT 1.077 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3130%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_6p1 += betrag
    data.append({'description': '', 'account': '3130', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': ''})
    # 3140
    sql_query = """SELECT 1.077 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3140%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_6p1 += betrag
    data.append({'description': '', 'account': '3140', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': ''})
    # total 6.1%
    tax_6p1 = summe_6p1 * 0.061
    data.append({'description': '', 'account': '<b>Total</b>', 'amount': "<b>CHF {:,.2f}</b>".format(summe_6p1).replace(",", "'"), 
                 'tax': "<b>CHF {:,.2f}</b>".format(tax_6p1).replace(",", "'") })
    # 3241
    summe_3p7 = 0.0
    sql_query = """SELECT 1.077 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3241%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_3p7 += betrag
    data.append({'description': '3.7%', 'account': '3241', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': ''})
    # total 3.7%
    tax_3p7 = summe_3p7 * 0.037
    data.append({'description': '', 'account': '<b>Total</b>', 'amount': "<b>CHF {:,.2f}</b>".format(summe_3p7).replace(",", "'"),
                 'tax': "<b>CHF {:,.2f}</b>".format(tax_3p7).replace(",", "'")})
    # 3210
    summe_2p1 = 0.0
    sql_query = """SELECT 1.025 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3210%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_2p1 += betrag
    data.append({'description': '2.1%', 'account': '3210', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': ''})
    # 3215
    sql_query = """SELECT 1.025 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3215%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_2p1 += betrag
    data.append({'description': '', 'account': '3215', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': ''})
    # total 2.1%
    tax_2p1 = summe_2p1 * 0.021
    data.append({'description': '', 'account': '<b>Total</b>', 'amount': "<b>CHF {:,.2f}</b>".format(summe_2p1).replace(",", "'"),
                 'tax': "<b>CHF {:,.2f}</b>".format(tax_2p1).replace(",", "'")})
    # 3200
    summe_0p6 = 0.0
    sql_query = """SELECT 1.025 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3200%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_0p6 += betrag
    data.append({'description': '0.6%', 'account': '3200', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': '' })
    # 3202
    sql_query = """SELECT 1.025 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3202%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_0p6 += betrag
    data.append({'description': '', 'account': '3202', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': '' })
    # 3204
    sql_query = """SELECT 1.025 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3204%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_0p6 += betrag
    data.append({'description': '', 'account': '3204', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': '' })
    # 3220
    sql_query = """SELECT 1.025 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3220%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_0p6 += betrag
    data.append({'description': '', 'account': '3220', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': '' })
    # 3230
    sql_query = """SELECT 1.025 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3230%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_0p6 += betrag
    data.append({'description': '0.6%', 'account': '3230', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': '' })
    # total 0.6%
    tax_0p6 = summe_0p6 * 0.006
    data.append({'description': '', 'account': '<b>Total</b>', 'amount': "<b>CHF {:,.2f}</b>".format(summe_0p6).replace(",", "'"),
                 'tax': "<b>CHF {:,.2f}</b>".format(tax_0p6).replace(",", "'") })
    # 3240
    summe_0p1 = 0.0
    sql_query = """SELECT 1.025 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3240%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_0p1 += betrag
    data.append({'description': '0.1%', 'account': '3240', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': '' })
    # total 0.1%
    tax_0p1 = summe_0p1 * 0.001
    data.append({'description': '', 'account': '<b>Total</b>', 'amount': "<b>CHF {:,.2f}</b>".format(summe_0p1).replace(",", "'"),
                 'tax': "<b>CHF {:,.2f}</b>".format(tax_0p1).replace(",", "'")})
    # summe umsätze
    total_summen = summe_6p1 + summe_3p7 + summe_2p1 + summe_0p6 + summe_0p1
    total_steuern = tax_6p1 + tax_3p7 + tax_2p1 + tax_0p6 + tax_0p1
    data.append({'description': '<b>Summe Umsätze</b>', 'account': '<b>(Ziffer 299)</b>', 'amount': "<b>CHF {:,.2f}</b>".format(total_summen).replace(",", "'"), 
                 'tax': "<b>CHF {:,.2f}</b>".format(total_steuern).replace(",", "'") })
    if total_summen > 0:
        avg_pps = (100 * total_steuern) / total_summen
    else:
        avg_pps = 0
    data.append({'description': 'Durchschnitts-PPS', 'account': '', 'amount': '', 'tax': "{:,.2f} %".format(avg_pps) })
    data.append({'description': '', 'account': '', 'amount': '', 'tax': ''})
    # excluded revenue
    data.append({'description': 'Ausgenommene Umsätze', 'account': '', 'amount': '', 'tax': ''})
    excluded = 0.0
    # 6810
    sql_query = """SELECT 1.0 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "6810%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    excluded += betrag
    data.append({'description': '', 'account': '6810', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': '' })
    # 6850
    sql_query = """SELECT 1.0 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "6850%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    excluded += betrag
    data.append({'description': '', 'account': '6850', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': '' })
    # total asugenommen
    data.append({'description': '<b>Total</b>', 'account': '<b>(Ziffer 230)</b>', 'amount': "<b>CHF {:,.2f}</b>".format(excluded).replace(",", "'"), 'tax': '' })
    # total Umsatz
    total_200 = excluded + total_summen
    data.append({'description': '<b>Total Umsatz</b>', 'account': '<b>(Ziffer 200)</b>', 'amount': "<b>CHF {:,.2f}</b>".format(total_200).replace(",", "'"), 'tax': ''})
    # subventionen
    sql_query = """SELECT 1.0 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3010%";""".format(from_date=from_date, to_date=to_date)
    subventionen = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    data.append({'description': '<b>Subventionen (Ziffer 900)</b>', 'account': '3010', 'amount': "<b>CHF {:,.2f}</b>".format(subventionen).replace(",", "'"), 'tax': '' })
    # spenden, beiträge GöV
    total_spenden = 0.0
    # 3000
    sql_query = """SELECT 1.0 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3000%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    total_spenden += betrag
    data.append({'description': 'Spenden, Beiträge GöV', 'account': '3000', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': ''})
    # 3020
    sql_query = """SELECT 1.0 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3020%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    total_spenden += betrag
    data.append({'description': '', 'account': '3020', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': '' })
    # 3030
    sql_query = """SELECT 1.0 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3030%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    total_spenden += betrag
    data.append({'description': '', 'account': '3030', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': '' })
    # 3040
    sql_query = """SELECT 1.0 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3040%";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    total_spenden += betrag
    data.append({'description': '', 'account': '3040', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': ''})
    # total spenden
    data.append({'description': '<b>Total Spenden</b>', 'account': '<b>(Ziffer 910)</b>', 
                 'amount': "<b>CHF {:,.2f}</b>".format(total_spenden).replace(",", "'"), 'tax': '' })
    # gesamtumsatz
    data.append({'description': '', 'account': '', 'amount': '', 'tax': ''})
    data.append({'description': '<b>Gesamtumsatz</b>', 'account': '', 
                 'amount': "<b>CHF {:,.2f}</b>".format(total_200 + subventionen + total_spenden).replace(",", "'"), 'tax': ''})
    
    return data
