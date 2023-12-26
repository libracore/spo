# Copyright (c) 2020-2023, libracore and contributors
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
        {"label": _("Betrag (brutto)"), "fieldname": "amount", "fieldtype": "Data", "width": 150},
        {"label": _("Steuer"), "fieldname": "tax", "fieldtype": "Data", "width": 150}
    ]

def get_data(from_date, to_date):
    data = []
    
    data.append({'description': '<b>Umsätze</b>', 'account': '<b>Konto</b>', 'amount': '<b>Betrag</b>', 'tax': '<b>Steuer</b>'})
    
    summe_6p1 = 0.0
    # 3100
    sql_query = """SELECT 1.081 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3101%SPO";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_6p1 += betrag
    data.append({'description': '6.2%', 'account': '3101', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': ''})
    # 3110
    sql_query = """SELECT 1.081 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3111%SPO";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_6p1 += betrag
    data.append({'description': '', 'account': '3111', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': ''})
    #3120
    sql_query = """SELECT 1.081 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3121%SPO";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_6p1 += betrag
    data.append({'description': '', 'account': '3121', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': ''})
    # 3130
    sql_query = """SELECT 1.081 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3131%SPO";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_6p1 += betrag
    data.append({'description': '', 'account': '3131', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': ''})
    # 3140
    sql_query = """SELECT 1.081 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3141%SPO";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    data.append({'description': '', 'account': '3141', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': ''})
    summe_6p1 += betrag
    # 3150
    sql_query = """SELECT 1.081 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3151%SPO";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_6p1 += betrag
    data.append({'description': '', 'account': '3151', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': ''})
    # 3160
    sql_query = """SELECT 1.081 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3161%SPO";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_6p1 += betrag
    data.append({'description': '', 'account': '3161', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': ''})
    # total 6.2% (formerly 5.9, formerly 6.1%)
    tax_6p1 = summe_6p1 * 0.062
    data.append({'description': '', 'account': '<b>Total</b>', 'amount': "<b>CHF {:,.2f}</b>".format(summe_6p1).replace(",", "'"), 
                 'tax': "<b>CHF {:,.2f}</b>".format(tax_6p1).replace(",", "'") })
    # 3241
    summe_3p7 = 0.0
    sql_query = """SELECT 1.081 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3242%SPO";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_3p7 += betrag
    data.append({'description': '3.7%', 'account': '3242', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': ''})
    # total 3.7% (formerly 3.5%, formerly 3.7%)
    tax_3p7 = summe_3p7 * 0.037
    data.append({'description': '', 'account': '<b>Total</b>', 'amount': "<b>CHF {:,.2f}</b>".format(summe_3p7).replace(",", "'"),
                 'tax': "<b>CHF {:,.2f}</b>".format(tax_3p7).replace(",", "'")})
    # 3210
    summe_2p1 = 0.0
    sql_query = """SELECT 1.026 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3211%SPO";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_2p1 += betrag
    data.append({'description': '2.1%', 'account': '3211', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': ''})
    # 3215
    sql_query = """SELECT 1.026 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3216%SPO";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_2p1 += betrag
    data.append({'description': '', 'account': '3216', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': ''})
    # total 2.1% (formerly 2.0%, formerly 2.1%)
    tax_2p1 = summe_2p1 * 0.021
    data.append({'description': '', 'account': '<b>Total</b>', 'amount': "<b>CHF {:,.2f}</b>".format(summe_2p1).replace(",", "'"),
                 'tax': "<b>CHF {:,.2f}</b>".format(tax_2p1).replace(",", "'")})
    # 3200
    summe_0p6 = 0.0
    sql_query = """SELECT 1.026 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3200%SPO";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_0p6 += betrag
    data.append({'description': '0.6%', 'account': '3200', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': '' })
    # 3202
    sql_query = """SELECT 1.026 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3202%SPO";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_0p6 += betrag
    data.append({'description': '', 'account': '3202', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': '' })
    # 3204
    sql_query = """SELECT 1.026 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3204%SPO";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_0p6 += betrag
    data.append({'description': '', 'account': '3204', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': '' })
    # 3220
    sql_query = """SELECT 1.026 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3220%SPO";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_0p6 += betrag
    data.append({'description': '', 'account': '3220', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': '' })
    # 3230
    sql_query = """SELECT 1.026 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3230%SPO";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    summe_0p6 += betrag
    data.append({'description': '', 'account': '3230', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': '' })
    # total 0.6%
    tax_0p6 = summe_0p6 * 0.006
    data.append({'description': '', 'account': '<b>Total</b>', 'amount': "<b>CHF {:,.2f}</b>".format(summe_0p6).replace(",", "'"),
                 'tax': "<b>CHF {:,.2f}</b>".format(tax_0p6).replace(",", "'") })
    # 3240
    summe_0p1 = 0.0
    sql_query = """SELECT 1.026 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3240%SPO";""".format(from_date=from_date, to_date=to_date)
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
                         AND `account` LIKE "6810%SPO";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    excluded += betrag
    data.append({'description': '', 'account': '6810', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': '' })
    # 6850
    sql_query = """SELECT 1.0 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "6850%SPO";""".format(from_date=from_date, to_date=to_date)
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
                         AND `account` LIKE "3010%SPO";""".format(from_date=from_date, to_date=to_date)
    subventionen = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    data.append({'description': '<b>Subventionen (Ziffer 900)</b>', 'account': '3010', 'amount': "<b>CHF {:,.2f}</b>".format(subventionen).replace(",", "'"), 'tax': '' })
    # spenden, beiträge GöV
    total_spenden = 0.0
    # 3000
    sql_query = """SELECT 1.0 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3000%SPO";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    total_spenden += betrag
    data.append({'description': 'Spenden, Beiträge GöV', 'account': '3000', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': ''})
    # 3020
    sql_query = """SELECT 1.0 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3020%SPO";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    total_spenden += betrag
    data.append({'description': '', 'account': '3020', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': '' })
    # 3030
    sql_query = """SELECT 1.0 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3030%SPO";""".format(from_date=from_date, to_date=to_date)
    betrag = frappe.db.sql(sql_query, as_dict=True)[0]['amount']
    total_spenden += betrag
    data.append({'description': '', 'account': '3030', 'amount': "CHF {:,.2f}".format(betrag).replace(",", "'"), 'tax': '' })
    # 3040
    sql_query = """SELECT 1.0 * IFNULL(SUM(`credit` - `debit`), 0) AS `amount` 
                   FROM `tabGL Entry` 
                   WHERE `posting_date` >= "{from_date}" 
                         AND `posting_date` <= "{to_date}" 
                         AND `account` LIKE "3040%SPO";""".format(from_date=from_date, to_date=to_date)
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
