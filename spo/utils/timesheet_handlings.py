# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import nowdate, add_to_date, get_datetime, get_datetime_str, time_diff_in_hours, get_time, add_days, getdate
from erpnext.projects.doctype.timesheet.timesheet import Timesheet
import json
from frappe.utils import flt

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
		ts.save()
			
	# check and submit ts:
	ts_list = frappe.db.sql("""SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 AND `start_date` < '{last_week}'""".format(last_week=add_days(nowdate(), -7)), as_dict=True)
	for _ts in ts_list:
		ts = frappe.get_doc("Timesheet", _ts.name)
		ruckmeldungen = 0
		arbeitszeit = 0
		for log in ts.time_logs:
			if log.activity_type != "Pause" and log.activity_type != "Arbeitszeit":
				ruckmeldungen += log.hours
		if ruckmeldungen <= ts.twh:
			ts.submit()
		#else:
			#mail versand wenn fehler....muss noch programmiert werden...
	
def get_zeiten_uebersicht(dt, name):
	if dt != 'Mandat':
		alle_zeiten = frappe.db.sql("""SELECT `parent`, `hours`, `from_time` FROM `tabTimesheet Detail` WHERE `spo_referenz` = '{name}' ORDER BY `from_time`""".format(name=name), as_dict=True)
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
def calc_arbeitszeit(employee, von, bis, uebertraege=None):
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
	# /Verhinderung von Jahresübergreifenden Abfragen
	#********************************
	#********************************
	# Variablen deklaration
	employee = frappe.get_doc("Employee", employee)
	arbeitszeit = 0
	sollzeit = 0
	anzahl_feiertage = 0
	anzahl_urlaubstage = 0
	anzahl_mo_bis_fr = 0
	anstellungsgrad = employee.anstellungsgrad
	tagesarbeitszeit = 8.4
	if employee.holiday_list:
		feiertagsliste = employee.holiday_list
	else:
		company = frappe.get_doc("Company", employee.company)
		feiertagsliste = company.default_holiday_list
	# /Variablen deklaration
	#********************************
	#********************************
	# Berechnung IST-Zeit
	# --> arbeitszeit
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
	# /Berechnung IST-Zeit
	#********************************
	#********************************
	# Berechnung Anzahl Feiertage und Krankheitstage (bei längerer Krankheit)
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
	# /Berechnung Anzahl Feiertage und Krankheitstage (bei längerer Krankheit)
	#********************************
	#********************************
	# Berechnung Anzahl Urlaubstage
	# --> ganztage
	bezogener_urlaub_in_tagen = []
	bezogene_urlaubs_perioden_ganztags = frappe.db.sql("""SELECT `from_date`, `to_date` FROM `tabLeave Application` WHERE `employee` = '{employee}' AND `half_day` = 0 AND `status` = 'Approved'""".format(employee=employee.name), as_dict=True)
	for bezogene_urlaubs_periode_ganztags in bezogene_urlaubs_perioden_ganztags:
		bezogener_urlaub_in_tagen.append(bezogene_urlaubs_periode_ganztags.from_date)
		bezogener_urlaub_in_tagen.append(bezogene_urlaubs_periode_ganztags.to_date)
		urlaub_von = add_days(getdate(bezogene_urlaubs_periode_ganztags.from_date), 1)
		urlaub_bis = getdate(bezogene_urlaubs_periode_ganztags.to_date)
		while urlaub_von < urlaub_bis:
			bezogener_urlaub_in_tagen.append(urlaub_von)
			urlaub_von = add_days(urlaub_von, 1)
	# --> halbtage
	bezogener_urlaub_in_halbtagen = []
	bezogene_urlaubs_perioden_halbtags = frappe.db.sql("""SELECT `from_date`, `to_date` FROM `tabLeave Application` WHERE `employee` = '{employee}' AND `half_day` = 1 AND `status` = 'Approved' AND `from_date` = `to_date`""".format(employee=employee.name), as_dict=True)
	for bezogene_urlaubs_periode_halbtags in bezogene_urlaubs_perioden_halbtags:
		bezogener_urlaub_in_halbtagen.append(bezogene_urlaubs_periode_halbtags.from_date)
	# --> gemischt
	bezogene_urlaubs_perioden_gemischt = frappe.db.sql("""SELECT `from_date`, `to_date`, `half_day_date` FROM `tabLeave Application` WHERE `employee` = '{employee}' AND `half_day` = 1 AND `status` = 'Approved' AND `from_date` != `to_date`""".format(employee=employee.name), as_dict=True)
	for bezogene_urlaubs_periode in bezogene_urlaubs_perioden_gemischt:
		urlaub_von = getdate(bezogene_urlaubs_periode.from_date)
		urlaub_bis = getdate(bezogene_urlaubs_periode.to_date)
		halbtag = getdate(bezogene_urlaubs_periode.half_day_date)
		while urlaub_von <= urlaub_bis:
			if urlaub_von != halbtag:
				bezogener_urlaub_in_tagen.append(urlaub_von)
			else:
				bezogener_urlaub_in_halbtagen.append(urlaub_von)
			urlaub_von = add_days(urlaub_von, 1)
	_von = getdate(von)
	_bis = getdate(bis)
	while _von <= _bis:
		if _von in bezogener_urlaub_in_tagen:
			anzahl_urlaubstage += 1
		if _von in bezogener_urlaub_in_halbtagen:
			anzahl_urlaubstage += 0.5
		_von = add_days(_von, 1)
	# /Berechnung Anzahl Urlaubstage
	#********************************
	#********************************
	# Berechnung Anzahl Mo - Fr
	_von = getdate(von)
	_bis = getdate(bis)
	while _von <= _bis:
		if _von.weekday() < 5:
			anzahl_mo_bis_fr += 1
		_von = add_days(_von, 1)
	# /Berechnung Anzahl Mo - Fr
	#********************************
	#********************************
	# Berechnung Sollzeit
	x = (anzahl_mo_bis_fr * tagesarbeitszeit) - (anzahl_feiertage * tagesarbeitszeit)
	y = (x / 100) * anstellungsgrad
	z = y - (anzahl_urlaubstage * tagesarbeitszeit)
	sollzeit = z
	# /Berechnung Sollzeit
	#********************************
	
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
