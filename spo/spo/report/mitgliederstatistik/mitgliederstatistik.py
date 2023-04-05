# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, month_diff, add_months, get_first_day, get_last_day

def execute(filters=None):
    check_date_range(filters)
    columns = get_columns(filters)
    data, chart_data = get_data(filters)
    
    if filters.einblenden:
        einblenden = filters.einblenden.split(",")
    else:
        einblenden = []
    
    label_dict = {
        'labels': [],
        'monate': []
    }
    
    for label in columns:
        if label['fieldname'] != 'bezugsdaten':
            label_dict['labels'].append(label['label'])
            label_dict['monate'].append(label['fieldname'])
    
    label_counter = 1
    datasets = []
    for data_set in chart_data:
        if len(einblenden) > 0:
            if str(label_counter) in einblenden:
                datasets.append({'name': str(label_counter), 'monat': data_set['data_set'], 'values': [], 'chartType': filters.chart_type.lower()})
        else:
            datasets.append({'name': str(label_counter), 'monat': data_set['data_set'], 'values': [], 'chartType': filters.chart_type.lower()})
        # ~ if data_set['data_set'] == 'Mitglieder':
            # ~ if int(mitglieder_ausblenden) != 1:
                # ~ datasets.append({'name': str(label_counter), 'monat': data_set['data_set'], 'values': [], 'chartType': 'bar'})
        # ~ else:
            # ~ datasets.append({'name': str(label_counter), 'monat': data_set['data_set'], 'values': [], 'chartType': 'bar'})
        label_counter += 1
    
    for label in label_dict['monate']:
        for data_set in datasets:
            for _data in chart_data:
                if _data['data_set'] == data_set['monat']:
                    for key in _data['values']:
                        if key == label:
                            data_set['values'].append(_data['values'][key])
    
    chart = {
        "data": {
            'labels': label_dict['labels'],
            'datasets': datasets
        },
        'type': 'axis-mixed',
        'colors': ["#b9fbc0", "#98f5e1", "#8A2BE2", "#90dbf4", "#a3c4f3", "#cfbaf0", "#f1c0e8", "#ffcfd2", "#fde4cf", "#fbf8cc"]
    }
    
    return columns, data, None, chart

def check_date_range(filters):
    start = getdate(filters.von)
    end = getdate(filters.bis)
    monats_differenz = month_diff(filters.bis, filters.von)
    
    if start > end:
        frappe.throw("Das Bis-Datum muss nach dem Start-Datum liegen.")
    
    if monats_differenz > 12:
        frappe.throw("Es darf maximal ein Zeitraum von 12 Monaten ausgewählt werden.")
    
    return

def get_columns(filters):
    start_month = getdate(filters.von).month
    end_month = getdate(filters.bis).month
    start_year = getdate(filters.von).year
    end_year = getdate(filters.bis).year
    
    if (end_month != start_month) or (start_year != end_year):
        end_month += 1
    
    columns = [{"label": _("Bezugsdaten"), "fieldname": "bezugsdaten", "fieldtype": "Data", "width": 285}]
    
    monats_columns = [
        {"label": _("Januar"), "fieldname": "jan", "fieldtype": "Data", "width": 85},
        {"label": _("Februar"), "fieldname": "feb", "fieldtype": "Data", "width": 85},
        {"label": _("März"), "fieldname": "mar", "fieldtype": "Data", "width": 85},
        {"label": _("April"), "fieldname": "apr", "fieldtype": "Data", "width": 85},
        {"label": _("Mai"), "fieldname": "mai", "fieldtype": "Data", "width": 85},
        {"label": _("Juni"), "fieldname": "jun", "fieldtype": "Data", "width": 85},
        {"label": _("Juli"), "fieldname": "jul", "fieldtype": "Data", "width": 85},
        {"label": _("August"), "fieldname": "aug", "fieldtype": "Data", "width": 85},
        {"label": _("September"), "fieldname": "sept", "fieldtype": "Data", "width": 85},
        {"label": _("Oktober"), "fieldname": "okt", "fieldtype": "Data", "width": 85},
        {"label": _("November"), "fieldname": "nov", "fieldtype": "Data", "width": 85},
        {"label": _("Dezember"), "fieldname": "dez", "fieldtype": "Data", "width": 85}
    ]
    
    if end_month > start_month:
        for month in range(start_month, end_month):
            columns.append(monats_columns[month - 1])
    elif (end_month == start_month) and (start_year == end_year):
        columns.append(monats_columns[start_month - 1])
    else:
        for month in range(start_month, 13):
            columns.append(monats_columns[month - 1])
        for month in range(1, end_month):
            columns.append(monats_columns[month - 1])
    
    return columns

def get_data(filters):
    data = []
    chart_data = []
    
    query_types = [
        'Mitglieder',
        'Auslaufende Mitgliedschaften ohne Verlängerung',
        'Auslaufende Mitgliedschaften mit Verlängerung',
        'Verlängerte Mitgliedschaften',
        'Neu-Mitglieder',
        'Kurz Mitglieder',
        'Erfasste Kündigungen',
        'Vollzogene Kündigungen',
        'Inaktivierungen',
        'Unbezahlt fristgerecht',
        'Unbezahlt gemahnt',
        'Unbezahlt Inaktivierungs-Vormerkung',
        'Total Unbezahlt'
    ]
    
    for query_type in query_types:
        query_data = get_query_data(filters, query_type)
        data.append(query_data)
        chart_data.append({
            'data_set': query_type,
            'values': query_data
        })
    
    return data, chart_data

def get_query_data(filters, query_type):
    data = {
        'bezugsdaten': query_type
    }
    
    start_date = getdate(filters.von)
    end_date = getdate(filters.bis)
    monats_differenz = month_diff(filters.bis, filters.von)
    
    if monats_differenz > 1:
        # start monat
        data[get_month(start_date.month)] = get_month_data(start_date, get_last_day(start_date), query_type)
        for month in range(1, monats_differenz):
            new_start = add_months(start_date, month)
            if (monats_differenz - 1) != month:
                # mittlere monate
                data[get_month(start_date.month + month)] = get_month_data(get_first_day(new_start), get_last_day(new_start), query_type)
            else:
                # end monat
                data[get_month(start_date.month + month)] = get_month_data(get_first_day(new_start), end_date, query_type)
    else:
        # einzelner monat
        data[get_month(start_date.month)] = get_month_data(start_date, end_date, query_type)
    
    return data

def get_month(month):
    if month > 12:
        month -= 12
    mapper = {
        1: 'jan',
        2: 'feb',
        3: 'mar',
        4: 'apr',
        5: 'mai',
        6: 'jun',
        7: 'jul',
        8: 'aug',
        9: 'sept',
        10: 'okt',
        11: 'nov',
        12: 'dez'
    }
    return mapper[month]

def get_month_data(start_date, end_date, query_type):
    if query_type == 'Mitglieder':
        return get_mitglieder(start_date, end_date)
    elif query_type == 'Neu-Mitglieder':
        return get_neu_mitglieder(start_date, end_date)
    elif query_type == 'Auslaufende Mitgliedschaften ohne Verlängerung':
        return get_auslaufende_mitgliedschaften(start_date, end_date)
    elif query_type == 'Auslaufende Mitgliedschaften mit Verlängerung':
        return get_auslaufende_mitgliedschaften_mit_verlaengerung(start_date, end_date)
    elif query_type == 'Verlängerte Mitgliedschaften':
        return get_verlaengerte_mitgliedschaften(start_date, end_date)
    elif query_type == 'Vollzogene Kündigungen':
        return get_kuendigungen(start_date, end_date)
    elif query_type == 'Erfasste Kündigungen':
        return get_erfasste_kuendigungen(start_date, end_date)
    elif query_type == 'Inaktivierungen':
        return get_inaktivierungen(start_date, end_date)
    elif query_type == 'Unbezahlt fristgerecht':
        return get_unbezahlt_fristgerecht(start_date, end_date)
    elif query_type == 'Unbezahlt gemahnt':
        return get_unbezahlt_gemahnt(start_date, end_date)
    elif query_type == 'Unbezahlt Inaktivierungs-Vormerkung':
        return get_unbezahlt_inaktivierungs_vormerkung(start_date, end_date)
    elif query_type == 'Total Unbezahlt':
        return get_unbezahlt(start_date, end_date)
    elif query_type == 'Kurz Mitglieder':
        return get_kurz_mitglieder(start_date, end_date)
    else:
        return 'Fehler'

def get_mitglieder(start_date, end_date):
    mitglieder =  frappe.db.sql("""
                            SELECT COUNT(`name`) AS `qty`
                            FROM `tabMitgliedschaft`
                            WHERE `start` < '{von}'
                            AND `ende` > '{bis}'""".format(von=start_date, bis=end_date), as_dict=True)[0].qty or 0
    
    # ~ auslaufend_verlaengert = frappe.db.sql("""
                            # ~ SELECT COUNT(`name`) AS `qty`
                            # ~ FROM `tabMitgliedschaft`
                            # ~ WHERE `ende` BETWEEN '{von}' AND '{bis}'
                            # ~ AND CAST(`not_renew` AS CHAR) != '1'""".format(von=start_date, bis=end_date), as_dict=True)[0].qty or 0
    
    # ~ return mitglieder + auslaufend_verlaengert
    return mitglieder

def get_kurz_mitglieder(start_date, end_date):
    kurz_mitglieder =  frappe.db.sql("""
                            SELECT COUNT(`name`) AS `qty`
                            FROM `tabMitgliedschaft`
                            WHERE `start` >= '{von}'
                            AND `ende` <= '{bis}'""".format(von=start_date, bis=end_date), as_dict=True)[0].qty or 0
    return kurz_mitglieder

def get_neu_mitglieder(start_date, end_date):
    qty = frappe.db.sql("""
                            SELECT 
                                COUNT(`alle`.`name`) AS `qty`
                            FROM `tabMitgliedschaft` AS `alle`
                            LEFT JOIN `tabMitgliedschaft` AS `verlaengerte` ON `alle`.`name` = `verlaengerte`.`neue_mitgliedschaft`
                            WHERE `alle`.`start` >= '{von}'
                            AND `alle`.`start` <= '{bis}'
                            AND `alle`.`ende` > '{bis}'
                            AND `verlaengerte`.`name` IS NULL""".format(von=start_date, bis=end_date), as_dict=True)[0].qty or 0
    return qty

def get_auslaufende_mitgliedschaften(start_date, end_date):
    return frappe.db.sql("""
                            SELECT COUNT(`name`) AS `qty`
                            FROM `tabMitgliedschaft`
                            WHERE `ende` BETWEEN '{von}' AND '{bis}'
                            AND `start` < '{von}'
                            AND CAST(`not_renew` AS CHAR) = '1'""".format(von=start_date, bis=end_date), as_dict=True)[0].qty or 0

def get_auslaufende_mitgliedschaften_mit_verlaengerung(start_date, end_date):
    return frappe.db.sql("""
                            SELECT COUNT(`name`) AS `qty`
                            FROM `tabMitgliedschaft`
                            WHERE `ende` BETWEEN '{von}' AND '{bis}'
                            AND `start` < '{von}'
                            AND CAST(`not_renew` AS CHAR) != '1'""".format(von=start_date, bis=end_date), as_dict=True)[0].qty or 0

def get_verlaengerte_mitgliedschaften(start_date, end_date):
    qty = frappe.db.sql("""
                            SELECT COUNT(`name`) AS `qty`
                            FROM `tabMitgliedschaft`
                            WHERE `start` >= '{von}'
                            AND `start` <= '{bis}'
                            AND `ende` > '{bis}'
                            AND `name` IN (
                                SELECT `neue_mitgliedschaft`
                                FROM `tabMitgliedschaft`
                            )""".format(von=start_date, bis=end_date), as_dict=True)[0].qty or 0
    return qty

def get_kuendigungen(start_date, end_date):
    return len(frappe.db.get_all('Mitgliedschaft', [
        ['ende', '>=', start_date],
        ['ende', '<=', end_date],
        ['status', '=', 'Kündigung']
    ])) or 0

def get_erfasste_kuendigungen(start_date, end_date):
    return len(frappe.db.get_all('Mitgliedschaft', [
        ['status_bezugsdatum', '>=', start_date],
        ['status_bezugsdatum', '<=', end_date],
        ['status', '=', 'Kündigung']
    ])) or 0

def get_inaktivierungen(start_date, end_date):
    return len(frappe.db.get_all('Mitgliedschaft', [
        ['status_bezugsdatum', '>=', start_date],
        ['status_bezugsdatum', '<=', end_date],
        ['status', '=', 'Inaktiviert']
    ])) or 0

def get_unbezahlt_fristgerecht(start_date, end_date):
    qty = frappe.db.sql("""
                            SELECT COUNT(`name`) AS `qty`
                            FROM `tabSales Invoice`
                            WHERE `status` != 'Paid'
                            AND `name` IN (
                                SELECT `rechnung`
                                FROM `tabMitgliedschaft`
                                WHERE `start` <= '{date}'
                                AND `ende` >= '{date}'
                            )
                            AND `payment_reminder_level` < 1""".format(date=start_date), as_dict=True)[0].qty or 0
    return qty

def get_unbezahlt_gemahnt(start_date, end_date):
    qty = frappe.db.sql("""
                            SELECT COUNT(`name`) AS `qty`
                            FROM `tabSales Invoice`
                            WHERE `status` != 'Paid'
                            AND `name` IN (
                                SELECT `rechnung`
                                FROM `tabMitgliedschaft`
                                WHERE `start` <= '{date}'
                                AND `ende` >= '{date}'
                            )
                            AND `payment_reminder_level`>= 1
                            AND `exclude_from_payment_reminder_until` IS NULL""".format(date=start_date), as_dict=True)[0].qty or 0
    return qty

def get_unbezahlt_inaktivierungs_vormerkung(start_date, end_date):
    qty = frappe.db.sql("""
                            SELECT COUNT(`name`) AS `qty`
                            FROM `tabSales Invoice`
                            WHERE `status` != 'Paid'
                            AND `name` IN (
                                SELECT `rechnung`
                                FROM `tabMitgliedschaft`
                                WHERE `start` <= '{date}'
                                AND `ende` >= '{date}'
                            )
                            AND `payment_reminder_level`>= 1
                            AND `exclude_from_payment_reminder_until` IS NOT NULL""".format(date=start_date), as_dict=True)[0].qty or 0
    return qty

def get_unbezahlt(start_date, end_date):
    qty = frappe.db.sql("""
                            SELECT COUNT(`name`) AS `qty`
                            FROM `tabSales Invoice`
                            WHERE `status` != 'Paid'
                            AND `name` IN (
                                SELECT `rechnung`
                                FROM `tabMitgliedschaft`
                                WHERE `start` <= '{date}'
                                AND `ende` >= '{date}'
                            )""".format(date=start_date), as_dict=True)[0].qty or 0
    return qty
