# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils.data import nowdate, add_to_date, get_datetime, get_datetime_str, time_diff_in_hours, get_time, add_days, getdate, date_diff
from erpnext.projects.doctype.timesheet.timesheet import Timesheet
import json
from frappe.utils import flt
from spo.utils.arbeitszeituebersicht_berechnung import berechnung_ist_zeit, anzahl_feiertage_und_krankheitstage, berechnung_anzahl_urlaubstage_ganz, berechnung_anzahl_mo_bis_fr, berechnung_sollzeit

@frappe.whitelist()
def handle_timesheet(user, doctype, reference, time, bemerkung='', date=nowdate()):
    _date = getdate(date)
    latest_date = getdate(add_days(nowdate(), -7))
    if _date < latest_date:
        frappe.throw("Sie können maximal 7 Tage in die Vergangenheit buchungen vornehmen.")
    user = frappe.db.sql("""SELECT `name` FROM `tabEmployee` WHERE `user_id` = '{user}'""".format(user=user), as_list=True)
    if not user:
        frappe.throw("Es wurde kein Mitarbeiterstamm gefunden!")
    else:
        user = user[0][0]
    if not time:
        time = 0.000
    else:
        time = float(time)
    ts = check_if_timesheet_exist(user, date)
    if ts == 'gebucht':
        frappe.throw("Das Timesheet vom {datum} ist bereits verbucht.".format(date=date))
    elif ts == 'neuanlage':
        create_timesheet(user, doctype, reference, time, bemerkung, date)
    else:
        update_timesheet(ts, time, doctype, reference, user, bemerkung, date)

def check_if_timesheet_exist(user, date):
    ts = frappe.db.sql("""SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 AND `employee` = '{user}' AND `start_date` = '{nowdate}'""".format(user=user, nowdate=date), as_dict=True)
    if len(ts) > 0:
        return ts[0].name
    else:
        ts = frappe.db.sql("""SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 1 AND `employee` = '{user}' AND `start_date` = '{nowdate}'""".format(user=user, nowdate=date), as_dict=True)
        if len(ts) > 0:
            return 'gebucht'
        else:
            return 'neuanlage'

def create_timesheet(user, doctype, reference, time, bemerkung, date):
    # check if first timesheet entry of reference
    existing_ts = frappe.db.sql("""SELECT `name` FROM `tabTimesheet` WHERE `docstatus` != 2 AND `name` IN (
                                    SELECT `parent` FROM `tabTimesheet Detail` WHERE `spo_referenz` = '{reference}')""".format(reference=reference), as_dict=True)
    if not len(existing_ts) > 0:
        default_time = get_default_time(doctype)
        if time < default_time:
            time = default_time

    start = date + " 00:00:00"
    type = 'Mandatsarbeit'
    if doctype == 'Anfrage':
        type = 'Beratung'
    ts = frappe.get_doc({
        "doctype": "Timesheet",
        "employee": user,
        "time_logs": [
            {
                "activity_type": type,
                "hours": time,
                "spo_dokument": doctype,
                "spo_referenz": reference,
                "from_time": get_datetime(get_datetime_str(start)),
                "spo_remark": bemerkung
            }
        ]
    })
    ts.insert(ignore_permissions=True)

def update_timesheet(ts, time, doctype, reference, user, bemerkung, date=None):
    #**********************************************************
    #overwrite the time_log overlap validation of timesheet
    overwrite_ts_validation()
    #**********************************************************

    # check if first timesheet entry of reference
    existing_ts = frappe.db.sql("""SELECT `name` FROM `tabTimesheet` WHERE `docstatus` != 2 AND `name` IN (
                            SELECT `parent` FROM `tabTimesheet Detail` WHERE `spo_referenz` = '{reference}')""".format(reference=reference), as_dict=True)
    if not len(existing_ts) > 0:
        default_time = get_default_time(doctype)
        if time < default_time:
            time = default_time

    ts = frappe.get_doc("Timesheet", ts)
    type = 'Mandatsarbeit'
    if doctype == 'Anfrage':
        type = 'Beratung'
    if not date:
        start = nowdate() + " 00:00:00"
    else:
        start = date + " 00:00:00"
    row = {}
    row["activity_type"] = type
    row["hours"] = time
    row["from_time"] = get_datetime(get_datetime_str(start))
    row["to_time"] = add_to_date(get_datetime(get_datetime_str(start)), hours=time)
    row["spo_dokument"] = doctype
    row["spo_referenz"] = reference
    row['spo_remark'] = bemerkung
    ts.append('time_logs', row)
    ts.save(ignore_permissions=True)

def get_default_time(doctype):
    time = 0
    defaults = frappe.get_doc("Einstellungen").ts_defaults
    for default in defaults:
        if default.dokument == doctype:
            time = default.default_hours
            break
    return time

@frappe.whitelist()
def get_total_ts_time(doctype, reference):
    if doctype != 'Mandat':
        time = float(frappe.db.sql("""SELECT SUM(`hours`) FROM `tabTimesheet Detail` WHERE `spo_dokument` = '{doctype}' AND `spo_referenz` = '{reference}' AND `parent` IN (
                            SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 OR `docstatus` = 1)""".format(doctype=doctype, reference=reference), as_list=True)[0][0] or 0)
        return time
    else:
        mandat = frappe.get_doc("Mandat", reference)
        referenz_anfrage = mandat.anfragen
        if referenz_anfrage:
            referenz_anfrage = " OR `spo_referenz` = '{referenz_anfrage}'".format(referenz_anfrage=referenz_anfrage)
        else:
            referenz_anfrage = ''
        time = float(frappe.db.sql("""SELECT SUM(`hours`) FROM `tabTimesheet Detail` WHERE
                                    `spo_referenz` = '{reference}'
                                    OR `spo_referenz` IN (
                                        SELECT `name` FROM `tabAnforderung Patientendossier` WHERE `mandat` = '{reference}')
                                    OR `spo_referenz` IN (
                                        SELECT `name` FROM `tabMedizinischer Bericht` WHERE `mandat` = '{reference}')
                                    OR `spo_referenz` IN (
                                        SELECT `name` FROM `tabTriage` WHERE `mandat` = '{reference}')
                                    OR `spo_referenz` IN (
                                        SELECT `name` FROM `tabVollmacht` WHERE `mandat` = '{reference}')
                                    OR `spo_referenz` IN (
                                        SELECT `name` FROM `tabAbschlussbericht` WHERE `mandat` = '{reference}'){referenz_anfrage}""".format(reference=reference, referenz_anfrage=referenz_anfrage), as_list=True)[0][0] or 0)
        return time

def overwrite_ts_validation():
    Timesheet.validate = ts_validation

def overwrite_ts_on_submit():
    Timesheet.on_submit = ts_on_submit

def ts_on_submit(self):
    #self.validate_mandatory_fields()
    self.update_task_and_project()

def ts_validation(self):
    #original timesheet validierung exkl. validate_time_logs()

    self.set_employee_name()
    self.set_status()
    self.validate_dates()
    #self.validate_time_logs()
    self.calculate_std_hours()
    #self.update_cost()
    self.calculate_total_amounts()
    self.calculate_percentage_billed()
    self.set_dates()

def auto_ts_submit():
    #************************************************************************************
    #overwrite the time_log overlap validation of timesheet and the on_submit validation
    overwrite_ts_validation()
    overwrite_ts_on_submit()
    #************************************************************************************
    
    unsaved_ts = []
    # correct twh:
    ts_list = frappe.db.sql("""SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 AND `start_date` < '{last_week}'""".format(last_week=add_days(nowdate(), -7)), as_dict=True)
    for _ts in ts_list:
        ts = frappe.get_doc("Timesheet", _ts.name)
        arbeitszeit = 0
        for log in ts.time_logs:
            if log.activity_type == "Arbeitszeit":
                arbeitszeit += log.hours
            if log.activity_type == "Pause":
                arbeitszeit -= log.hours
        ts.twh = arbeitszeit
        try:
            ts.save()
        except Exception as err:
            unsaved_ts.append([ts.name, err])
            continue
    
    unsubmitted_ts = []
    # check and submit ts:
    ts_list = frappe.db.sql("""SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 AND `start_date` < '{last_week}'""".format(last_week=add_days(nowdate(), -7)), as_dict=True)
    for _ts in ts_list:
        ts = frappe.get_doc("Timesheet", _ts.name)
        ruckmeldungen = 0
        arbeitszeit = 0
        for log in ts.time_logs:
            if log.activity_type != "Pause" and log.activity_type != "Arbeitszeit":
                ruckmeldungen += log.hours
        if float(ruckmeldungen) <= float(ts.twh):
            try:
                ts.submit()
            except Exception as err:
                unsubmitted_ts.append([ts.name, ruckmeldungen, ts.twh, err])
                continue
        else:
            unsubmitted_ts.append([ts.name, ruckmeldungen, ts.twh, 'Rückmeldung > Arbeitszeit'])
    
    if len(unsaved_ts) > 0 or len(unsubmitted_ts) > 0:
        error_msg = ''
        if len(unsaved_ts) > 0:
            error_msg += "Nachfolgende Timesheets konnten nicht gespeichert werden (TS, (Fehler)):\n"
            for u_ts in unsaved_ts:
                error_msg += '{0} ({1})\n'.format(u_ts[0], u_ts[1])
        if len(unsubmitted_ts) > 0:
            error_msg += "\nNachfolgende Timesheets konnten nicht gebucht werden werden (TS, Arbeitszeit, Rückmeldungen, (Fehler):)\n"
            for u_ts in unsubmitted_ts:
                error_msg += '{0}, {1}, {2}, {3}\n'.format(u_ts[0], u_ts[2], u_ts[1], u_ts[3])
        frappe.log_error("{0}".format(error_msg), 'Auto TS Submit')

def get_zeiten_uebersicht(dt, name):
    if dt != 'Mandat':
        alle_zeiten = frappe.db.sql("""SELECT `parent`, `hours`, `from_time`, `spo_referenz`, `spo_dokument`, `spo_remark` FROM `tabTimesheet Detail` WHERE `spo_referenz` = '{name}' ORDER BY `from_time`""".format(name=name), as_dict=True)
        return alle_zeiten
    else:
        mandat = frappe.get_doc("Mandat", name)
        referenz_anfrage = mandat.anfragen
        if referenz_anfrage:
            referenz_anfrage = " OR `spo_referenz` = '{referenz_anfrage}'".format(referenz_anfrage=referenz_anfrage)
        else:
            referenz_anfrage = ''
        alle_zeiten = frappe.db.sql("""SELECT `parent`, `hours`, `from_time`, `spo_referenz`, `spo_dokument`, `spo_remark` FROM `tabTimesheet Detail` WHERE
                                        `spo_referenz` = '{name}'
                                        OR `spo_referenz` IN (
                                            SELECT `name` FROM `tabAnforderung Patientendossier` WHERE `mandat` = '{name}')
                                        OR `spo_referenz` IN (
                                            SELECT `name` FROM `tabMedizinischer Bericht` WHERE `mandat` = '{name}')
                                        OR `spo_referenz` IN (
                                            SELECT `name` FROM `tabTriage` WHERE `mandat` = '{name}')
                                        OR `spo_referenz` IN (
                                            SELECT `name` FROM `tabVollmacht` WHERE `mandat` = '{name}')
                                        OR `spo_referenz` IN (
                                            SELECT `name` FROM `tabAbschlussbericht` WHERE `mandat` = '{name}'){referenz_anfrage} ORDER BY `from_time`, `spo_referenz`""".format(name=name, referenz_anfrage=referenz_anfrage), as_dict=True)
        return alle_zeiten

@frappe.whitelist()
def check_ts_owner(ts, user):
    ts = frappe.get_doc("Timesheet", ts)
    employee = frappe.get_doc("Employee", ts.employee)
    user_id = employee.user_id
    if user_id == user:
        return True
    else:
        return False

@frappe.whitelist()
def calc_arbeitszeit(employee, von, bis, uebertraege=None, anstellungsgrade=None, urlaubslisten=None):
    '''
        Variablenübersicht:
        IST = Berechnung IST-Zeit (--> arbeitszeit (ist inkl. uebertraege))
        Anzahl Feiertage = Berechnung Anzahl Feiertage + Anzahl Krankheitstage (--> anzahl_feiertage)
        Anzahl Urlaubstage = Berechnung Anzahl Urlaubstage (--> anzahl_urlaubstage)
        Anzahl Mo - Fr = Berechnung Anzahl Mo - Fr (--> anzahl_mo_bis_fr)
        Anstellungsgrad in % (--> anstellungsgrad)
        Tagesarbeitszeit (-->tagesarbeitszeit)
        
        Sollzeitberechnung:
        x = ((Anzahl Mo - Fr) * Tagesarbeitszeit) - ((Anzahl Feiertage) * Tagesarbeitszeit)
        y = x * (Anstellungsgrad in %)
        z = y - ((Anzahl Urlaubstage) * Tagesarbeitszeit)
        Sollzeit = z (--> sollzeit)
    '''
    #********************************
    # Verhinderung von Jahresübergreifenden Abfragen
    if getdate(von).year != getdate(bis).year:
        return 'jahr'
    #********************************

    employee = frappe.get_doc("Employee", employee)
    arbeitszeit = berechnung_ist_zeit(employee, von, bis, uebertraege)
    
    tagesarbeitszeit = 8.4
    
    feiertagsliste = False
    aktuelles_jahr = getdate(nowdate()).year
    if getdate(von).year == aktuelles_jahr:
        if employee.holiday_list:
            feiertagsliste = employee.holiday_list
        else:
            company = frappe.get_doc("Company", employee.company)
            feiertagsliste = company.default_holiday_list
    else:
        urlaubslisten = json.loads(urlaubslisten)
        for urlaubsliste in urlaubslisten:
            if getdate(urlaubsliste["von"]).year == getdate(von).year:
                feiertagsliste = urlaubsliste["holiday_list"]
        if not feiertagsliste:
            frappe.throw(_("Sie haben für die gewählte Periode keine Urlaubsliste hinterlegt"))
    
    
    
    anstellungsgrade_gewaehltes_jahr = []
    anstellungsgrad_gefunden = False
    anstellungsgrade = json.loads(anstellungsgrade)
    for _anstellungsgrad in anstellungsgrade:
        if getdate(von).year == getdate(_anstellungsgrad["von"]).year:
            anstellungsgrad_gefunden = True
            anstellungsgrade_gewaehltes_jahr.append([_anstellungsgrad["von"], _anstellungsgrad["bis"], _anstellungsgrad["anstellungsgrad"]])
    if not anstellungsgrad_gefunden:
        if employee.anstellungsgrad:
            anstellungsgrad = employee.anstellungsgrad
            multi = False
            anzahl_mo_bis_fr = berechnung_anzahl_mo_bis_fr(von, bis)
            anzahl_feiertage = anzahl_feiertage_und_krankheitstage(von, bis, feiertagsliste)
        else:
            frappe.throw(_("Sie haben für die gewählte Periode keinen Anstellungsgrad hinterlegt"))
    else:
        if len(anstellungsgrade_gewaehltes_jahr) > 1:
            anstellungsgrad = []
            multi = True
            for agj in anstellungsgrade_gewaehltes_jahr:
                s1 = getdate(von)
                e1 = getdate(bis)
                s2 = getdate(agj[0])
                e2 = getdate(agj[1])
                do_append = True
                
                if (e2 < s1):
                    do_append = False
                if (s2 > e1):
                    do_append = False
                if (s2 == s1) and (e2 < e1):
                    anzahl_mo_bis_fr = berechnung_anzahl_mo_bis_fr(von, agj[1])
                    anzahl_feiertage = anzahl_feiertage_und_krankheitstage(von, agj[1], feiertagsliste)
                if (s2 == s1) and (e2 > e1):
                    anzahl_mo_bis_fr = berechnung_anzahl_mo_bis_fr(von, bis)
                    anzahl_feiertage = anzahl_feiertage_und_krankheitstage(von, bis, feiertagsliste)
                if (s2 == s1) and (e2 == e1):
                    anzahl_mo_bis_fr = berechnung_anzahl_mo_bis_fr(von, bis)
                    anzahl_feiertage = anzahl_feiertage_und_krankheitstage(von, bis, feiertagsliste)
                if (s2 < s1) and (e2 < e1):
                    anzahl_mo_bis_fr = berechnung_anzahl_mo_bis_fr(von, agj[1])
                    anzahl_feiertage = anzahl_feiertage_und_krankheitstage(von, agj[1], feiertagsliste)
                if (s2 < s1) and (e2 > e1):
                    anzahl_mo_bis_fr = berechnung_anzahl_mo_bis_fr(von, bis)
                    anzahl_feiertage = anzahl_feiertage_und_krankheitstage(von, bis, feiertagsliste)
                if (s2 < s1) and (e2 == e1):
                    anzahl_mo_bis_fr = berechnung_anzahl_mo_bis_fr(von, bis)
                    anzahl_feiertage = anzahl_feiertage_und_krankheitstage(von, bis, feiertagsliste)
                if (s1 < s2) and (e2 < e1):
                    anzahl_mo_bis_fr = berechnung_anzahl_mo_bis_fr(agj[0], agj[1])
                    anzahl_feiertage = anzahl_feiertage_und_krankheitstage(agj[0], agj[1], feiertagsliste)
                if (s1 < s2) and (e2 > e1):
                    anzahl_mo_bis_fr = berechnung_anzahl_mo_bis_fr(agj[0], bis)
                    anzahl_feiertage = anzahl_feiertage_und_krankheitstage(agj[0], bis, feiertagsliste)
                if (s1 < s2) and (e2 == e1):
                    anzahl_mo_bis_fr = berechnung_anzahl_mo_bis_fr(agj[0], bis)
                    anzahl_feiertage = anzahl_feiertage_und_krankheitstage(agj[0], bis, feiertagsliste)
                
                if do_append:
                    try:
                        anstellungsgrad.append([anzahl_mo_bis_fr, anzahl_feiertage, agj[2]])
                    except:
                        frappe.throw("s1 = {s1}, e1 = {e1}, s2 = {s2}, e2 = {e2}".format(s1=s1, s2=s2, e1=e1, e2=e2))
        else:
            anstellungsgrad = anstellungsgrade_gewaehltes_jahr[0][2]
            multi = False
            anzahl_mo_bis_fr = berechnung_anzahl_mo_bis_fr(von, bis)
            anzahl_feiertage = anzahl_feiertage_und_krankheitstage(von, bis, feiertagsliste)
    
    anzahl_urlaubstage = berechnung_anzahl_urlaubstage_ganz(von, bis, employee)
    if not multi:
        sollzeit = berechnung_sollzeit(anzahl_mo_bis_fr=anzahl_mo_bis_fr, tagesarbeitszeit=tagesarbeitszeit, anzahl_feiertage=anzahl_feiertage, anstellungsgrad=anstellungsgrad, anzahl_urlaubstage=anzahl_urlaubstage, multi=multi)
    else:
        sollzeit = berechnung_sollzeit(tagesarbeitszeit=tagesarbeitszeit, anstellungsgrad=anstellungsgrad, anzahl_urlaubstage=anzahl_urlaubstage, multi=multi)

    return {
            'arbeitszeit': str(round(arbeitszeit, 3)),
            'sollzeit': str(round(sollzeit, 3)),
            'diff': str(round(arbeitszeit - sollzeit, 3))
        }

@frappe.whitelist()
def get_pending_leaves_for_current_year(employee, date):
    ''' Returns leaves that are pending approval '''
    urlaub = frappe.db.get_value("Leave Application",
        filters={
            "employee": employee,
            "leave_type": 'Urlaub',
            "from_date": (">=", getdate(str(getdate(date).year) + '-01-01')),
            "to_date": ("<=", getdate(str(getdate(date).year) + '-12-31')),
            "status": "Open"
        }, fieldname=['SUM(total_leave_days)']) or flt(0)
        
    persoenlich = frappe.db.get_value("Leave Application",
        filters={
            "employee": employee,
            "leave_type": 'Persönlich',
            "from_date": (">=", getdate(str(getdate(date).year) + '-01-01')),
            "to_date": ("<=", getdate(str(getdate(date).year) + '-12-31')),
            "status": "Open"
        }, fieldname=['SUM(total_leave_days)']) or flt(0)
        
    return {
            'urlaub': str(urlaub),
            'persoenlich': str(persoenlich)
        }

def create_default_ts_entry(user, doctype, record, datum, onlineberatung=False):
    #**********************************************************
    #overwrite the time_log overlap validation of timesheet
    overwrite_ts_validation()
    #**********************************************************

    datum = getdate(datum)
    latest_date = getdate(add_days(nowdate(), -7))
    if datum < latest_date:
        frappe.throw("Die Erfassung der standardzeit in Ihrem Timesheet konnte nicht erfasst werden, da das Datum weiter zurück als 7 Tage liegt.")
    user = frappe.db.sql("""SELECT `name` FROM `tabEmployee` WHERE `user_id` = '{user}'""".format(user=user), as_list=True)
    if not user:
        frappe.throw("Es wurde kein Mitarbeiterstamm gefunden!")
    else:
        user = user[0][0]
    if not onlineberatung:
        time = get_default_time(doctype)
    else:
        time = 0.5
    ts = frappe.db.sql("""SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 1 AND `employee` = '{user}' AND `start_date` = '{nowdate}'""".format(user=user, nowdate=datum.strftime("%Y-%m-%d")), as_dict=True)
    if len(ts) > 0:
        frappe.throw("Das Timesheet vom {datum} ist bereits verbucht.".format(datum=datum))
    else:
        ts = frappe.db.sql("""SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 AND `employee` = '{user}' AND `start_date` = '{nowdate}'""".format(user=user, nowdate=datum.strftime("%Y-%m-%d")), as_dict=True)
        if len(ts) > 0:
            ts = frappe.get_doc("Timesheet", ts[0].name)
            type = 'Mandatsarbeit'
            if doctype == 'Anfrage':
                type = 'Beratung'
            start = datum.strftime("%Y-%m-%d") + " 00:00:00"
            row = {}
            row["activity_type"] = type
            row["hours"] = time
            row["from_time"] = get_datetime(get_datetime_str(start))
            row["to_time"] = add_to_date(get_datetime(get_datetime_str(start)), hours=time)
            row["spo_dokument"] = doctype
            row["spo_referenz"] = record
            row['spo_remark'] = ''
            ts.append('time_logs', row)
            ts.save(ignore_permissions=True)
        else:
            start = datum.strftime("%Y-%m-%d") + " 00:00:00"
            type = 'Mandatsarbeit'
            if doctype == 'Anfrage':
                type = 'Beratung'
            ts = frappe.get_doc({
                "doctype": "Timesheet",
                "employee": user,
                "time_logs": [
                    {
                        "activity_type": type,
                        "hours": time,
                        "spo_dokument": doctype,
                        "spo_referenz": record,
                        "from_time": get_datetime(get_datetime_str(start)),
                        "spo_remark": ''
                    }
                ]
            })
            ts.insert(ignore_permissions=True)
            
    frappe.db.commit()

@frappe.whitelist()
def create_ts_entry(user, doctype, record, datum, time, bemerkung='', nicht_verrechnen=0):
    #**********************************************************
    #overwrite the time_log overlap validation of timesheet
    overwrite_ts_validation()
    #**********************************************************
    time = float(time)
    datum = getdate(datum)
    latest_date = getdate(add_days(nowdate(), -7))
    if datum < latest_date:
        frappe.throw("Die Erfassung der standardzeit in Ihrem Timesheet konnte nicht erfasst werden, da das Datum weiter zurück als 7 Tage liegt.")
    user = frappe.db.sql("""SELECT `name` FROM `tabEmployee` WHERE `user_id` = '{user}'""".format(user=user), as_list=True)
    if not user:
        frappe.throw("Es wurde kein Mitarbeiterstamm gefunden!")
    else:
        user = user[0][0]
    #time = get_default_time(doctype)
    ts = frappe.db.sql("""SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 1 AND `employee` = '{user}' AND `start_date` = '{nowdate}'""".format(user=user, nowdate=datum.strftime("%Y-%m-%d")), as_dict=True)
    if len(ts) > 0:
        frappe.throw("Das Timesheet vom {datum} ist bereits verbucht.".format(datum=datum))
    else:
        ts = frappe.db.sql("""SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 AND `employee` = '{user}' AND `start_date` = '{nowdate}'""".format(user=user, nowdate=datum.strftime("%Y-%m-%d")), as_dict=True)
        if len(ts) > 0:
            ts = frappe.get_doc("Timesheet", ts[0].name)
            type = 'Mandatsarbeit'
            if doctype == 'Anfrage':
                type = 'Beratung'
            start = datum.strftime("%Y-%m-%d") + " 00:00:00"
            row = {}
            row["activity_type"] = type
            row["hours"] = time
            row["from_time"] = get_datetime(get_datetime_str(start))
            row["to_time"] = add_to_date(get_datetime(get_datetime_str(start)), hours=time)
            row["spo_dokument"] = doctype
            row["spo_referenz"] = record
            row['spo_remark'] = bemerkung
            row['nicht_verrechnen'] = nicht_verrechnen
            ts.append('time_logs', row)
            ts.save(ignore_permissions=True)
        else:
            start = datum.strftime("%Y-%m-%d") + " 00:00:00"
            type = 'Mandatsarbeit'
            if doctype == 'Anfrage':
                type = 'Beratung'
            ts = frappe.get_doc({
                "doctype": "Timesheet",
                "employee": user,
                "time_logs": [
                    {
                        "activity_type": type,
                        "hours": time,
                        "spo_dokument": doctype,
                        "spo_referenz": record,
                        "from_time": get_datetime(get_datetime_str(start)),
                        "spo_remark": bemerkung,
                        "nicht_verrechnen": nicht_verrechnen
                    }
                ]
            })
            ts.insert(ignore_permissions=True)
            
    frappe.db.commit()
