# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import nowdate, add_to_date, get_datetime, get_datetime_str, time_diff_in_hours, get_time, add_days, getdate, date_diff
from erpnext.projects.doctype.timesheet.timesheet import Timesheet
import json
from frappe.utils import flt

def berechnung_ist_zeit(employee, von, bis, uebertraege):
    arbeitszeit = 0
    timesheets = frappe.db.sql("""SELECT `name` FROM `tabTimesheet` WHERE `employee` = '{employee}' AND `start_date` >= '{von}' AND `start_date` <= '{bis}' AND `docstatus` != 2""".format(employee=employee.name, von=von, bis=bis), as_dict=True)
    for ts in timesheets:
        ts = frappe.get_doc("Timesheet", ts.name)
        for log in ts.time_logs:
            if log.activity_type == 'Arbeitszeit':
                arbeitszeit += log.hours
            if log.activity_type == 'Pause':
                arbeitszeit -= log.hours
    # --> berücksichtigung überträge
    if uebertraege:
        _bis = getdate(bis)
        uebertraege = json.loads(uebertraege)
        for saldo in uebertraege:
            if saldo["uebertrag_auf_jahr"] == str(_bis.year):
                arbeitszeit += float(saldo["stunden"])
    return arbeitszeit

def anzahl_feiertage_und_krankheitstage(von, bis, feiertagsliste):
    anzahl_feiertage = 0
    # --> Ganztage
    holidays = frappe.db.sql("""SELECT COUNT(`name`) FROM `tabHoliday` WHERE `holiday_date` >= '{von}' AND `holiday_date` <= '{bis}' AND `half_day` = 0 AND `parent` = '{feiertagsliste}' AND `percentage_sick` = 0""".format(von=von, bis=bis, feiertagsliste=feiertagsliste), as_list=True)
    if holidays:
        holidays = holidays[0][0]
    else:
        holidays = 0
    anzahl_feiertage += holidays
    # --> Halbtage
    holidays = frappe.db.sql("""SELECT COUNT(`name`) FROM `tabHoliday` WHERE `holiday_date` >= '{von}' AND `holiday_date` <= '{bis}' AND `half_day` = 1 AND `parent` = '{feiertagsliste}' AND `percentage_sick` = 0""".format(von=von, bis=bis, feiertagsliste=feiertagsliste), as_list=True)
    if holidays:
        holidays = holidays[0][0] / 2
    else:
        holidays = 0
    anzahl_feiertage += holidays
    # --> krankheitstage != 100% (=Ganztage) & != 50% (=Halbtage)
    holidays = frappe.db.sql("""SELECT `sick_percentage` FROM `tabHoliday` WHERE `holiday_date` >= '{von}' AND `holiday_date` <= '{bis}' AND `half_day` = 0 AND `parent` = '{feiertagsliste}' AND `percentage_sick` = 1""".format(von=von, bis=bis, feiertagsliste=feiertagsliste), as_dict=True)
    if holidays:
        for holiday in holidays:
            anzahl_feiertage += (holiday.sick_percentage / 100)
    return anzahl_feiertage
            
def berechnung_anzahl_urlaubstage_ganz(von, bis, employee):
    anzahl_urlaubstage = 0
    # ganze Tage:
    # --> innerhalb periode
    innerhalb = frappe.db.sql("""SELECT `total_leave_days` FROM `tabLeave Application` WHERE `from_date` >= '{von}' AND `to_date` <= '{bis}' AND `employee` = '{employee}' AND `half_day` = 0 AND `status` = 'Approved' AND `docstatus` = 1""".format(von=von, bis=bis, employee=employee.name), as_dict=True)
    if innerhalb:
        for bezogene_urlaubs_tage in innerhalb:
            anzahl_urlaubstage += bezogene_urlaubs_tage.total_leave_days
    # --> start ausserhalb periode
    ausserhalb = frappe.db.sql("""SELECT `to_date` FROM `tabLeave Application` WHERE `from_date` < '{von}' AND `to_date` <= '{bis}' AND `to_date` >= '{von}' AND `employee` = '{employee}' AND `half_day` = 0 AND `status` = 'Approved' AND `docstatus` = 1""".format(von=von, bis=bis, employee=employee.name), as_dict=True)
    if ausserhalb:
        for bezogene_urlaubs_tage in ausserhalb:
            anzahl_urlaubstage += date_diff(bezogene_urlaubs_tage.to_date, von) + 1
    # --> ende ausserhalb periode
    ende_ausserhalb = frappe.db.sql("""SELECT `from_date` FROM `tabLeave Application` WHERE `from_date` >= '{von}' AND `from_date` <= '{bis}' AND `to_date` > '{bis}' AND `employee` = '{employee}' AND `half_day` = 0 AND `status` = 'Approved' AND `docstatus` = 1""".format(von=von, bis=bis, employee=employee.name), as_dict=True)
    if ende_ausserhalb:
        for bezogene_urlaubs_tage in ende_ausserhalb:
            anzahl_urlaubstage += date_diff(bis, bezogene_urlaubs_tage.from_date) + 1
    # --> start und ende ausserhalb periode
    # sollte es nie geben.

    # halbe Tage
    # --> innerhalb periode
    halbe_innerhalb = frappe.db.sql("""SELECT `total_leave_days` FROM `tabLeave Application` WHERE `from_date` >= '{von}' AND `to_date` <= '{bis}' AND `employee` = '{employee}' AND `half_day` = 1 AND `status` = 'Approved' AND `docstatus` = 1""".format(von=von, bis=bis, employee=employee.name), as_dict=True)
    if halbe_innerhalb:
        for bezogene_urlaubs_tage in halbe_innerhalb:
            anzahl_urlaubstage += bezogene_urlaubs_tage.total_leave_days
    # --> start ausserhalb periode
    halbe_ausserhalb = frappe.db.sql("""SELECT `to_date`, `half_day_date` FROM `tabLeave Application` WHERE `from_date` < '{von}' AND `to_date` <= '{bis}' AND `to_date` >= '{von}' AND `employee` = '{employee}' AND `half_day` = 1 AND `status` = 'Approved' AND `docstatus` = 1""".format(von=von, bis=bis, employee=employee.name), as_dict=True)
    if halbe_ausserhalb:
        for bezogene_urlaubs_tage in halbe_ausserhalb:
            if getdate(bezogene_urlaubs_tage.half_day_date) >= getdate(von):
                anzahl_urlaubstage += date_diff(bezogene_urlaubs_tage.to_date, von) + 0.5
            else:
                anzahl_urlaubstage += date_diff(bezogene_urlaubs_tage.to_date, von) + 1
    # --> ende ausserhalb periode
    halbe_ende_ausserhalb = frappe.db.sql("""SELECT `from_date`, `half_day_date` FROM `tabLeave Application` WHERE `from_date` >= '{von}' AND `from_date` <= '{bis}' AND `to_date` > '{bis}' AND `employee` = '{employee}' AND `half_day` = 1 AND `status` = 'Approved' AND `docstatus` = 1""".format(von=von, bis=bis, employee=employee.name), as_dict=True)
    if halbe_ende_ausserhalb:
        for bezogene_urlaubs_tage in halbe_ende_ausserhalb:
            if getdate(bezogene_urlaubs_tage.half_day_date) <= getdate(bis):
                anzahl_urlaubstage += date_diff(bis, bezogene_urlaubs_tage.from_date) + 0.5
            else:
                anzahl_urlaubstage += date_diff(bis, bezogene_urlaubs_tage.from_date) + 1
    # --> start und ende ausserhalb periode
    # sollte es nie geben.
    return anzahl_urlaubstage
    
def berechnung_anzahl_mo_bis_fr(von, bis):
    anzahl_mo_bis_fr = 0
    _von = getdate(von)
    _bis = getdate(bis)
    while _von <= _bis:
        if _von.weekday() < 5:
            anzahl_mo_bis_fr += 1
        _von = add_days(_von, 1)
    return anzahl_mo_bis_fr
        
def berechnung_sollzeit(anzahl_mo_bis_fr=None, tagesarbeitszeit=None, anzahl_feiertage=None, anstellungsgrad=None, anzahl_urlaubstage=None, multi=None):
    if not multi:
        x = (anzahl_mo_bis_fr * tagesarbeitszeit) - (anzahl_feiertage * tagesarbeitszeit)
        y = (x / 100) * anstellungsgrad
        z = y - (anzahl_urlaubstage * tagesarbeitszeit)
        return z
    else:
        y = 0
        for ag in anstellungsgrad:
            x = (ag[0] * tagesarbeitszeit) - (ag[1] * tagesarbeitszeit)
            y += (x / 100) * ag[2]
        z = y - (anzahl_urlaubstage * tagesarbeitszeit)
        return z