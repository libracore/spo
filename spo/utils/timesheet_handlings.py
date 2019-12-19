# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import nowdate, add_to_date, get_datetime, get_datetime_str, time_diff_in_hours, get_time, add_days
from erpnext.projects.doctype.timesheet.timesheet import Timesheet

@frappe.whitelist()
def handle_timesheet(user, doctype, reference, time, bemerkung=''):
	user = frappe.db.sql("""SELECT `name` FROM `tabEmployee` WHERE `user_id` = '{user}'""".format(user=user), as_list=True)
	if not time:
		time = 0
	time = float(time)
	if user:
		user = user[0][0]
		ts = check_if_timesheet_exist(user, doctype, reference)
		if ts:
			if doctype == 'Mandat':
				update_mandat_timesheet(ts, time, doctype, reference, user, bemerkung)
			else:
				update_timesheet(ts, time, doctype, reference, user)
		else:
			if doctype == 'Mandat':
				create_mandat_timesheet(user, doctype, reference, time, bemerkung)
			else:
				create_timesheet(user, doctype, reference, time)
	else:
		return False
	
def check_if_timesheet_exist(user, doctype, reference):
	ts = frappe.db.sql("""SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 AND `employee` = '{user}' AND `start_date` = '{nowdate}'""".format(user=user, nowdate=nowdate()), as_dict=True)
	if len(ts) > 0:
		return ts[0].name
	else:
		return False
	
def create_timesheet(user, doctype, reference, time):
	default_time = get_default_time(doctype)
	if time < default_time:
		time = default_time
	start = nowdate() + " 00:00:00"
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
				"from_time": get_datetime(get_datetime_str(start))
			}
		]
	})
	ts.insert(ignore_permissions=True)
	
def create_mandat_timesheet(user, doctype, reference, time, bemerkung):
	default_time = get_default_time(doctype)
	if time < default_time:
		time = default_time
	start = nowdate() + " 00:00:00"
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
	
def update_timesheet(ts, time, doctype, reference, user):
	#**********************************************************
	#overwrite the time_log overlap validation of timesheet
	overwrite_ts_validation()
	#**********************************************************
	
	ts = frappe.get_doc("Timesheet", ts)
	ref_time_log_found = False
	for time_log in ts.time_logs:
		if time_log.activity_type != 'Arbeitszeit' and time_log.activity_type != 'Pause':
			if time_log.spo_dokument == doctype:
				if time_log.spo_referenz == reference:
					if (time + time_log.hours) > get_default_time(doctype):
						time_log.hours = time + time_log.hours
						ref_time_log_found = True
	
	if ref_time_log_found:
		ts.save(ignore_permissions=True)
	else:
		type = 'Mandatsarbeit'
		if doctype == 'Anfrage':
			type = 'Beratung'
		start = nowdate() + " 00:00:00"
		row = {}
		row["activity_type"] = type
		if (time) > get_default_time(doctype):
			row["hours"] = time
		else:
			row["hours"] = get_default_time(doctype)
		row["from_time"] = get_datetime(get_datetime_str(start))
		row["to_time"] = add_to_date(get_datetime(get_datetime_str(start)), hours=time)
		row["spo_dokument"] = doctype
		row["spo_referenz"] = reference
		ts.append('time_logs', row)
		ts.save(ignore_permissions=True)
		
def update_mandat_timesheet(ts, time, doctype, reference, user, bemerkung):
	#**********************************************************
	#overwrite the time_log overlap validation of timesheet
	overwrite_ts_validation()
	#**********************************************************
	
	ts = frappe.get_doc("Timesheet", ts)
	type = 'Mandatsarbeit'
	start = nowdate() + " 00:00:00"
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
	
def cleanup_ts(user):
	#**********************************************************
	#overwrite the time_log overlap validation of timesheet
	overwrite_ts_validation()
	#**********************************************************
	
	all_ts = frappe.db.sql("""SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 AND `employee` = '{user}' AND `start_date` = '{nowdate}'""".format(user=user, nowdate=nowdate()), as_dict=True)
	all_time_logs = []
	for _ts in all_ts:
		ts = frappe.get_doc("Timesheet", _ts.name)
		for time_log in ts.time_logs:
			all_time_logs.append(time_log)
			
	for _ts in all_ts:
		ts = frappe.get_doc("Timesheet", _ts.name)
		ts.delete(ignore_permissions=True)
			
	new_ts = frappe.get_doc({
		"doctype": "Timesheet",
		"employee": user,
		"time_logs": []
	})
	start = nowdate() + " 00:00:00"
	for time_log in all_time_logs:
		if time_log.activity_type != 'Arbeitszeit' and time_log.activity_type != 'Pause':
			time_log.from_time = start
			time_log.to_time = add_to_date(start, hours=time_log.hours)
			new_ts.time_logs.append(time_log)
			start = add_to_date(start, hours=time_log.hours + 0.001)
		else:
			new_ts.time_logs.append(time_log)
	new_ts.insert(ignore_permissions=True)
	
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
	
	
	ts_list = frappe.db.sql("""SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 AND `start_date` < '{last_week}'""".format(last_week=add_days(nowdate(), -7)), as_dict=True)
	for _ts in ts_list:
		ts = frappe.get_doc("Timesheet", _ts.name)
		ts.submit()
	
def get_zeiten_uebersicht(dt, name):
	if dt != 'Mandat':
		alle_zeiten = frappe.db.sql("""SELECT `parent`, `hours`, `from_time` FROM `tabTimesheet Detail` WHERE `spo_referenz` = '{name}'""".format(name=name), as_dict=True)
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
											SELECT `name` FROM `tabAbschlussbericht` WHERE `mandat` = '{name}'){referenz_anfrage} ORDER BY `spo_referenz`""".format(name=name, referenz_anfrage=referenz_anfrage), as_dict=True)
		return alle_zeiten