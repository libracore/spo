# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.hr.doctype.leave_application.leave_application import get_leave_details
from frappe.utils.data import nowdate, add_to_date, get_datetime, get_datetime_str, time_diff_in_hours, get_time, add_days, getdate, date_diff
from frappe.utils import flt
from spo.utils.arbeitszeituebersicht_berechnung import berechnung_ist_zeit, anzahl_feiertage_und_krankheitstage, berechnung_anzahl_urlaubstage_ganz, berechnung_anzahl_mo_bis_fr, berechnung_sollzeit

def execute(filters=None):
    columns, data = ["Mitarbeiter:Link/Employee:200", "Name:Data:200"], []
    employee_filter = ''
    if filters.employee:
        employee_filter = """ AND `name` = '{employee}'""".format(employee=filters.employee)
        
    employees = frappe.db.sql("""SELECT `name`, `employee_name`, `anstellungsgrad`, `company`, `holiday_list`, `anstellung`, `date_of_joining` FROM `tabEmployee` WHERE `status` = 'Active'{employee_filter}""".format(employee_filter=employee_filter), as_dict=True)
    activity_types = frappe.db.sql("""SELECT `name` FROM `tabActivity Type` ORDER BY `name` ASC""", as_dict=True)
    for act_type in activity_types:
        if act_type.name == 'Arbeitszeit':
            columns.append("Präsenzzeit:Float:50")
        else:
            columns.append(act_type.name + ":Float:50")
        
    '''	
        Sollzeitberechnung (gem. DaTa):
        x = ((Anzahl Mo - Fr) * Tagesarbeitszeit) - ((Anzahl Feiertage) * Tagesarbeitszeit)
        y = x * (Anstellungsgrad in %)
        z = y - ((Anzahl Urlaubstage) * Tagesarbeitszeit)
        Sollzeit = z (--> sollzeit)
    '''

    for employee in employees:
        # brücksichtigung von Eintrittsdatum
        filters_from_date = filters.from_date
        if employee.date_of_joining > getdate(filters.from_date):
            filters_from_date = employee.date_of_joining
        
        data_to_append = []
        data_to_append.append(employee.name)
        data_to_append.append(employee.employee_name)
        total_arbeitszeit = 0
        total_rueckmeldungen = 0
        ganze_feiertage = 0
        halbe_feiertage = 0
        prozentuale_feiertage = 0
        feiertage = 0
        urlaub = 0
        urlaub_total = 0.00
        _urlaub_total = get_leave_details(employee=employee.name, date=getdate(filters.to_date))
        if _urlaub_total['leave_allocation']:
            for ut in _urlaub_total['leave_allocation']:
                urlaub_total += float(_urlaub_total['leave_allocation'][ut]['total_leaves'])
        gleitzeit = 0
        
        # Timelogs:
        for act_type in activity_types:
            time_logs = frappe.db.sql("""SELECT SUM(`hours`) FROM `tabTimesheet Detail` WHERE `activity_type` = '{act_type}' AND DATE(`from_time`) >= '{von}' AND DATE(`from_time`) <= '{bis}' AND `parent` IN (
                                            SELECT `name` FROM `tabTimesheet` WHERE `employee` = '{employee}' AND `docstatus` != 2)""".format(von=filters_from_date, bis=filters.to_date, act_type=act_type.name, employee=employee.name), as_list=True)
            if time_logs[0][0]:
                data_to_append.append(time_logs[0][0])
                if act_type.name == 'Arbeitszeit':
                    total_arbeitszeit += time_logs[0][0]
                elif act_type.name == 'Pause':
                    total_arbeitszeit -= time_logs[0][0]
                else:
                    total_rueckmeldungen += time_logs[0][0]
            else:
                data_to_append.append(0.00)
        data_to_append.append(total_arbeitszeit)
        data_to_append.append(total_rueckmeldungen)
        
        # Feiertage:
        # wenn employee nicht stundenlohn:
        if employee.anstellung != 'Stundenlohn':
            default_holiday_list = frappe.get_doc("Company", employee.company).default_holiday_list
            if employee.holiday_list:
                default_holiday_list = employee.holiday_list

            ganze_feiertage = frappe.db.sql("""SELECT COUNT(`name`) FROM `tabHoliday` WHERE `half_day` = 0 AND `holiday_date` BETWEEN '{von}' AND '{bis}' AND `parent` = '{default_holiday_list}' AND `percentage_sick` = 0""".format(von=filters_from_date, bis=filters.to_date, default_holiday_list=default_holiday_list), as_list=True)
            if ganze_feiertage[0][0]:
                ganze_feiertage = ganze_feiertage[0][0]
            else:
                ganze_feiertage = 0
                
            halbe_feiertage = frappe.db.sql("""SELECT COUNT(`name`) FROM `tabHoliday` WHERE `half_day` = 1 AND `holiday_date` BETWEEN '{von}' AND '{bis}' AND `parent` = '{default_holiday_list}' AND `percentage_sick` = 0""".format(von=filters_from_date, bis=filters.to_date, default_holiday_list=default_holiday_list), as_list=True)
            if halbe_feiertage[0][0]:
                halbe_feiertage = halbe_feiertage[0][0] / 2
            else:
                halbe_feiertage = 0
                
            prozentuale_feiertage = frappe.db.sql("""SELECT SUM(`sick_percentage`) FROM `tabHoliday` WHERE `holiday_date` BETWEEN '{von}' AND '{bis}' AND `parent` = '{default_holiday_list}' AND `percentage_sick` = 1""".format(von=filters_from_date, bis=filters.to_date, default_holiday_list=default_holiday_list), as_list=True)
            if prozentuale_feiertage[0][0]:
                prozentuale_feiertage = ((8.4 / 100) * prozentuale_feiertage[0][0]) / 8.4
            else:
                prozentuale_feiertage = 0
                
            feiertage = ganze_feiertage + halbe_feiertage + prozentuale_feiertage
            data_to_append.append(feiertage)
        
        
            # Urlaub:
            urlaub = frappe.db.sql("""SELECT SUM(`total_leave_days`) FROM `tabLeave Application` WHERE `employee` = '{employee}' AND `status` = 'Approved' AND `docstatus` = 1 AND `from_date` BETWEEN '{von}' AND '{bis}'""".format(employee=employee.name, von=filters_from_date, bis=filters.to_date), as_list=True)
            if urlaub[0][0]:
                urlaub = urlaub[0][0]
            else:
                urlaub = 0
            data_to_append.append(urlaub)
            data_to_append.append(urlaub_total)
            
            _sollzeit = get_sollzeit(employee.name, filters_from_date, filters.to_date)
            
            data_to_append.append(_sollzeit)
            
            #übertrag aus vorjahr
            uebertrag = 0
            uebertraege = frappe.db.sql("""SELECT `uebertrag_auf_jahr`, `stunden` FROM `tabVorjahressaldo` WHERE `parent` = '{employee}'""".format(employee=employee.name), as_dict=True)
            for _uebertrag in uebertraege:
                if getdate(filters_from_date).strftime("%Y") == _uebertrag["uebertrag_auf_jahr"]:
                    uebertrag += float(_uebertrag["stunden"])
            
            data_to_append.append(uebertrag)
            
            # gleitzeit
            gleitzeit = (total_arbeitszeit - _sollzeit) + uebertrag
            data_to_append.append(gleitzeit)
            
        #wenn employee == Stundenlohn:
        else:
            data_to_append.append(0.00)
            data_to_append.append(0.00)
            data_to_append.append(0.00)
            data_to_append.append(0.00)
            
            #übertrag aus vorjahr
            uebertrag = 0
            uebertraege = frappe.db.sql("""SELECT `uebertrag_auf_jahr`, `stunden` FROM `tabVorjahressaldo` WHERE `parent` = '{employee}'""".format(employee=employee.name), as_dict=True)
            for _uebertrag in uebertraege:
                if getdate(filters_from_date).strftime("%Y") == _uebertrag["uebertrag_auf_jahr"]:
                    uebertrag += float(_uebertrag["stunden"])
            data_to_append.append(uebertrag)
            
            data_to_append.append(total_arbeitszeit + uebertrag)
        
        # Add MA row to all Rows
        data.append(data_to_append)
        
    columns.append("Summe Arbeitszeit:Float")
    columns.append("Summe Rückmeldungen:Float")
    columns.append("Feiertage:Float")
    columns.append("Bezogener Urlaub:Float")
    columns.append("Total Urlaub:Float")
    columns.append("Sollzeit:Float")
    columns.append("Übertrag:Float")
    columns.append("Gleitzeit:Float")
    return columns, data

def get_sollzeit(employee, von, bis):
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
    employee = frappe.get_doc("Employee", employee)
    anstellungsgrade = employee.anstellungsgrade
    urlaubslisten = employee.urlaubslisten
    
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
        #urlaubslisten = json.loads(urlaubslisten)
        for urlaubsliste in urlaubslisten:
            if getdate(urlaubsliste.von).year == getdate(von).year:
                feiertagsliste = urlaubsliste.holiday_list
        if not feiertagsliste:
            frappe.throw(_("Sie haben für die gewählte Periode im Mitarbeiterstamm {ma} keine Urlaubsliste hinterlegt".format(ma=employee.name)))
    
    
    
    anstellungsgrade_gewaehltes_jahr = []
    anstellungsgrad_gefunden = False
    for _anstellungsgrad in anstellungsgrade:
        if getdate(von).year == getdate(_anstellungsgrad.von).year:
            anstellungsgrad_gefunden = True
            anstellungsgrade_gewaehltes_jahr.append([_anstellungsgrad.von, _anstellungsgrad.bis, _anstellungsgrad.anstellungsgrad])
    if not anstellungsgrad_gefunden:
        if employee.anstellungsgrad:
            anstellungsgrad = employee.anstellungsgrad
            multi = False
            anzahl_mo_bis_fr = berechnung_anzahl_mo_bis_fr(von, bis)
            anzahl_feiertage = anzahl_feiertage_und_krankheitstage(von, bis, feiertagsliste)
        else:
            frappe.throw(_("Sie haben für die gewählte Periode im Mitarbeiterstamm {ma} keinen Anstellungsgrad hinterlegt".format(ma=employee.name)))
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

    return round(sollzeit, 3)
