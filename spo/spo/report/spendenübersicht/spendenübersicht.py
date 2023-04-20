# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import now_datetime, get_last_day
from frappe import _

def execute(filters=None):
    if filters.ansicht == '5 Jahre jährlich':
        return five_years(filters)
    if filters.ansicht == '1 Jahr monatlich':
        return one_year(filters)

def five_years(filters=None):
    current_year = int(now_datetime().strftime('%Y'))
    last_year = current_year - 1
    second_last_year = current_year - 2
    third_last_year = current_year -  3
    fourth_last_year = current_year - 4
    fifth_last_year = current_year - 5

    columns, data = [
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer"},
        {"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data"},
        {"label": str(current_year), "fieldname": str(current_year), "fieldtype": "Float", "width": 100},
        {"label": str(last_year), "fieldname": str(last_year), "fieldtype": "Float", "width": 100},
        {"label": str(second_last_year), "fieldname": str(second_last_year), "fieldtype": "Float", "width": 100},
        {"label": str(third_last_year), "fieldname": str(third_last_year), "fieldtype": "Float", "width": 100},
        {"label": str(fourth_last_year), "fieldname": str(fourth_last_year), "fieldtype": "Float", "width": 100},
        {"label": str(fifth_last_year), "fieldname": str(fifth_last_year), "fieldtype": "Float", "width": 100},
        {"label": "Total {current_year} - {fifth_last_year}".format(current_year=current_year, fifth_last_year=fifth_last_year), "fieldname": "total", "fieldtype": "Float"}
    ], []

    all_customer = frappe.db.sql("""SELECT `name`, `customer_name` FROM `tabCustomer`""", as_dict=True)

    for customer in all_customer:
        all_payment_entries_current = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND YEAR(`posting_date`) = '{year}'""".format(customer=customer.name, year=current_year)
        all_payment_entries_current_1 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND YEAR(`posting_date`) = '{year}'""".format(customer=customer.name, year=last_year)
        all_payment_entries_current_2 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND YEAR(`posting_date`) = '{year}'""".format(customer=customer.name, year=second_last_year)
        all_payment_entries_current_3 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND YEAR(`posting_date`) = '{year}'""".format(customer=customer.name, year=third_last_year)
        all_payment_entries_current_4 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND YEAR(`posting_date`) = '{year}'""".format(customer=customer.name, year=fourth_last_year)
        all_payment_entries_current_5 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND YEAR(`posting_date`) = '{year}'""".format(customer=customer.name, year=fifth_last_year)
        
        spende_current = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount' FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=all_payment_entries_current), as_dict=True)
        spende_current_1 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount'  FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=all_payment_entries_current_1), as_dict=True)
        spende_current_2 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount'  FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=all_payment_entries_current_2), as_dict=True)
        spende_current_3 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount'  FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=all_payment_entries_current_3), as_dict=True)
        spende_current_4 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount'  FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=all_payment_entries_current_4), as_dict=True)
        spende_current_5 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount'  FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=all_payment_entries_current_5), as_dict=True)
        
        total = 0
        
        _data = []
        _data.append(customer.name)
        _data.append(customer.customer_name)
        if spende_current[0].amount:
            _data.append(spende_current[0].amount * -1)
            total += spende_current[0].amount * -1
        else:
            _data.append('0.00')
        if spende_current_1[0].amount:
            _data.append(spende_current_1[0].amount * -1)
            total += spende_current_1[0].amount * -1
        else:
            _data.append('0.00')
        if spende_current_2[0].amount:
            _data.append(spende_current_2[0].amount * -1)
            total += spende_current_2[0].amount * -1
        else:
            _data.append('0.00')
        if spende_current_3[0].amount:
            _data.append(spende_current_3[0].amount * -1)
            total += spende_current_3[0].amount * -1
        else:
            _data.append('0.00')
        if spende_current_4[0].amount:
            _data.append(spende_current_4[0].amount * -1)
            total += spende_current_4[0].amount * -1
        else:
            _data.append('0.00')
        if spende_current_5[0].amount:
            _data.append(spende_current_5[0].amount * -1)
            total += spende_current_5[0].amount * -1
        else:
            _data.append('0.00')
        _data.append(total)
        data.append(_data)
    return columns, data

def one_year(filters=None):
    current_year = int(now_datetime().strftime('%Y'))
    if int(filters.bezugsjahr) > 0:
        current_year = int(filters.bezugsjahr)
    
    month_1 = "{0}-01-01".format(current_year)
    month_1_end = get_last_day(month_1)
    month_2 = "{0}-02-01".format(current_year)
    month_2_end = get_last_day(month_2)
    month_3 = "{0}-03-01".format(current_year)
    month_3_end = get_last_day(month_3)
    month_4 = "{0}-04-01".format(current_year)
    month_4_end = get_last_day(month_4)
    month_5 = "{0}-05-01".format(current_year)
    month_5_end = get_last_day(month_5)
    month_6 = "{0}-06-01".format(current_year)
    month_6_end = get_last_day(month_6)
    month_7 = "{0}-07-01".format(current_year)
    month_7_end = get_last_day(month_7)
    month_8 = "{0}-08-01".format(current_year)
    month_8_end = get_last_day(month_8)
    month_9 = "{0}-09-01".format(current_year)
    month_9_end = get_last_day(month_9)
    month_10 = "{0}-10-01".format(current_year)
    month_10_end = get_last_day(month_10)
    month_11 = "{0}-11-01".format(current_year)
    month_11_end = get_last_day(month_11)
    month_12 = "{0}-12-01".format(current_year)
    month_12_end = get_last_day(month_12)
    
    label_month_1 = "Januar"
    label_month_2 = "Februar"
    label_month_3 = "März"
    label_month_4 = "April"
    label_month_5 = "Mai"
    label_month_6 = "Juni"
    label_month_7 = "Juli"
    label_month_8 = "August"
    label_month_9 = "September"
    label_month_10 = "Oktober"
    label_month_11 = "November"
    label_month_12 = "Dezember"

    columns, data = [
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer"},
        {"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data"},
        {"label": label_month_1, "fieldname": label_month_1, "fieldtype": "Float", "width": 100},
        {"label": label_month_2, "fieldname": label_month_2, "fieldtype": "Float", "width": 100},
        {"label": label_month_3, "fieldname": label_month_3, "fieldtype": "Float", "width": 100},
        {"label": label_month_4, "fieldname": label_month_4, "fieldtype": "Float", "width": 100},
        {"label": label_month_5, "fieldname": label_month_5, "fieldtype": "Float", "width": 100},
        {"label": label_month_6, "fieldname": label_month_6, "fieldtype": "Float", "width": 100},
        {"label": label_month_7, "fieldname": label_month_7, "fieldtype": "Float", "width": 100},
        {"label": label_month_8, "fieldname": label_month_8, "fieldtype": "Float", "width": 100},
        {"label": label_month_9, "fieldname": label_month_9, "fieldtype": "Float", "width": 100},
        {"label": label_month_10, "fieldname": label_month_10, "fieldtype": "Float", "width": 100},
        {"label": label_month_11, "fieldname": label_month_11, "fieldtype": "Float", "width": 100},
        {"label": label_month_12, "fieldname": label_month_12, "fieldtype": "Float", "width": 100},
        {"label": "Total {current_year}".format(current_year=current_year), "fieldname": "total", "fieldtype": "Float"}
    ], []

    all_customer = frappe.db.sql("""SELECT `name`, `customer_name` FROM `tabCustomer`""", as_dict=True)

    for customer in all_customer:
        payments_month_1 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND `posting_date` BETWEEN '{month_1}' AND '{month_1_end}'""".format(customer=customer.name, month_1=month_1, month_1_end=month_1_end)
        payments_month_2 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND `posting_date` BETWEEN '{month_2}' AND '{month_2_end}'""".format(customer=customer.name, month_2=month_2, month_2_end=month_2_end)
        payments_month_3 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND `posting_date` BETWEEN '{month_3}' AND '{month_3_end}'""".format(customer=customer.name, month_3=month_3, month_3_end=month_3_end)
        payments_month_4 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND `posting_date` BETWEEN '{month_4}' AND '{month_4_end}'""".format(customer=customer.name, month_4=month_4, month_4_end=month_4_end)
        payments_month_5 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND `posting_date` BETWEEN '{month_5}' AND '{month_5_end}'""".format(customer=customer.name, month_5=month_5, month_5_end=month_5_end)
        payments_month_6 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND `posting_date` BETWEEN '{month_6}' AND '{month_6_end}'""".format(customer=customer.name, month_6=month_6, month_6_end=month_6_end)
        payments_month_7 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND `posting_date` BETWEEN '{month_7}' AND '{month_7_end}'""".format(customer=customer.name, month_7=month_7, month_7_end=month_7_end)
        payments_month_8 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND `posting_date` BETWEEN '{month_8}' AND '{month_8_end}'""".format(customer=customer.name, month_8=month_8, month_8_end=month_8_end)
        payments_month_9 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND `posting_date` BETWEEN '{month_9}' AND '{month_9_end}'""".format(customer=customer.name, month_9=month_9, month_9_end=month_9_end)
        payments_month_10 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND `posting_date` BETWEEN '{month_10}' AND '{month_10_end}'""".format(customer=customer.name, month_10=month_10, month_10_end=month_10_end)
        payments_month_11 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND `posting_date` BETWEEN '{month_11}' AND '{month_11_end}'""".format(customer=customer.name, month_11=month_11, month_11_end=month_11_end)
        payments_month_12 = """SELECT `name` FROM `tabPayment Entry` WHERE `payment_type` = 'Receive' AND `party` = '{customer}' AND `docstatus` = 1 AND `posting_date` BETWEEN '{month_12}' AND '{month_12_end}'""".format(customer=customer.name, month_12=month_12, month_12_end=month_12_end)
        
        spende_month_1 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount' FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=payments_month_1), as_dict=True)
        spende_month_2 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount' FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=payments_month_2), as_dict=True)
        spende_month_3 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount' FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=payments_month_3), as_dict=True)
        spende_month_4 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount' FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=payments_month_4), as_dict=True)
        spende_month_5 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount' FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=payments_month_5), as_dict=True)
        spende_month_6 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount' FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=payments_month_6), as_dict=True)
        spende_month_7 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount' FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=payments_month_7), as_dict=True)
        spende_month_8 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount' FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=payments_month_8), as_dict=True)
        spende_month_9 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount' FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=payments_month_9), as_dict=True)
        spende_month_10 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount' FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=payments_month_10), as_dict=True)
        spende_month_11 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount' FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=payments_month_11), as_dict=True)
        spende_month_12 = frappe.db.sql("""SELECT SUM(`amount`) AS 'amount' FROM `tabPayment Entry Deduction` WHERE `parent` IN ({payment_query}) AND `parentfield` = 'deductions' AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(payment_query=payments_month_12), as_dict=True)
        
        total = 0
        
        _data = []
        _data.append(customer.name)
        _data.append(customer.customer_name)
        
        if spende_month_1[0].amount:
            _data.append(spende_month_1[0].amount * -1)
            total += spende_month_1[0].amount * -1
        else:
            _data.append('0.00')
        if spende_month_2[0].amount:
            _data.append(spende_month_2[0].amount * -1)
            total += spende_month_2[0].amount * -1
        else:
            _data.append('0.00')
        if spende_month_3[0].amount:
            _data.append(spende_month_3[0].amount * -1)
            total += spende_month_3[0].amount * -1
        else:
            _data.append('0.00')
        if spende_month_4[0].amount:
            _data.append(spende_month_4[0].amount * -1)
            total += spende_month_4[0].amount * -1
        else:
            _data.append('0.00')
        if spende_month_5[0].amount:
            _data.append(spende_month_5[0].amount * -1)
            total += spende_month_5[0].amount * -1
        else:
            _data.append('0.00')
        if spende_month_6[0].amount:
            _data.append(spende_month_6[0].amount * -1)
            total += spende_month_6[0].amount * -1
        else:
            _data.append('0.00')
        if spende_month_7[0].amount:
            _data.append(spende_month_7[0].amount * -1)
            total += spende_month_7[0].amount * -1
        else:
            _data.append('0.00')
        if spende_month_8[0].amount:
            _data.append(spende_month_8[0].amount * -1)
            total += spende_month_8[0].amount * -1
        else:
            _data.append('0.00')
        if spende_month_9[0].amount:
            _data.append(spende_month_9[0].amount * -1)
            total += spende_month_9[0].amount * -1
        else:
            _data.append('0.00')
        if spende_month_10[0].amount:
            _data.append(spende_month_10[0].amount * -1)
            total += spende_month_10[0].amount * -1
        else:
            _data.append('0.00')
        if spende_month_11[0].amount:
            _data.append(spende_month_11[0].amount * -1)
            total += spende_month_11[0].amount * -1
        else:
            _data.append('0.00')
        if spende_month_12[0].amount:
            _data.append(spende_month_12[0].amount * -1)
            total += spende_month_12[0].amount * -1
        else:
            _data.append('0.00')
        
        _data.append(total)
        data.append(_data)
    return columns, data
