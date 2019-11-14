# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import nowdate, add_to_date, get_datetime, get_datetime_str
from erpnext.projects.doctype.timesheet.timesheet import Timesheet

@frappe.whitelist()
def handle_timesheet(user, doctype, reference, time):
	user = frappe.db.sql("""SELECT `name` FROM `tabEmployee` WHERE `user_id` = '{user}'""".format(user=user), as_list=True)
	if not time:
		time = 0
	time = float(time)
	if user:
		user = user[0][0]
		ts = check_if_timesheet_exist(user, doctype, reference)
		if ts:
			update_timesheet(ts, time, doctype, reference, user)
		else:
			create_timesheet(user, doctype, reference, time)
	else:
		return False
	
def check_if_timesheet_exist(user, doctype, reference):
	ts = frappe.db.sql("""SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 AND `employee` = '{user}'""".format(user=user), as_dict=True)
	if len(ts) > 0:
		return ts[0].name
	else:
		return False
	
def create_timesheet(user, doctype, reference, time):
	default_time = get_default_time(doctype)
	if time < default_time:
		time = default_time
	start = nowdate() + " 00:00:00"
	ts = frappe.get_doc({
		"doctype": "Timesheet",
		"employee": user,
		"time_logs": [
			{
				"activity_type": "Execution",
				"hours": time,
				"spo_dokument": doctype,
				"spo_referenz": reference,
				"from_time": get_datetime(get_datetime_str(start))
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
		if time_log.activity_type != 'Kommen/gehen':
			if time_log.spo_dokument == doctype:
				if time_log.spo_referenz == reference:
					if (time + time_log.hours) > get_default_time(doctype):
						time_log.hours = time + time_log.hours
						ref_time_log_found = True
	
	if ref_time_log_found:
		ts.save(ignore_permissions=True)
	else:
		start = nowdate() + " 00:00:00"
		row = {}
		row["activity_type"] = 'Execution'
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
	
	all_ts = frappe.db.sql("""SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 AND `employee` = '{user}'""".format(user=user), as_dict=True)
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
		if time_log.activity_type != 'Kommen/Gehen':
			time_log.from_time = start
			time_log.to_time = add_to_date(start, hours=time_log.hours)
			new_ts.time_logs.append(time_log)
			start = add_to_date(start, hours=time_log.hours + 0.001)
		else:
			new_ts.time_logs.append(time_log)
	new_ts.insert(ignore_permissions=True)
	
@frappe.whitelist()
def get_total_ts_time(doctype, reference):
	time = float(frappe.db.sql("""SELECT SUM(`hours`) FROM `tabTimesheet Detail` WHERE `spo_dokument` = '{doctype}' AND `spo_referenz` = '{reference}' AND `parent` IN (
						SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 OR `docstatus` = 1)""".format(doctype=doctype, reference=reference), as_list=True)[0][0] or 0)
	return time
	
@frappe.whitelist()
def sollzeit(ts=None, user=None, typ='Kommen/Gehen', time='00:00:00', insert_first=False):
	if not user:
		return False
		
	#**********************************************************
	#overwrite the time_log overlap validation of timesheet
	overwrite_ts_validation()
	#**********************************************************
	
	if ts:
		ts = frappe.get_doc("Timesheet", ts)
	else:
		user = frappe.db.sql("""SELECT `name` FROM `tabEmployee` WHERE `user_id` = '{user}'""".format(user=user), as_list=True)[0][0]
		ts = frappe.db.sql("""SELECT DISTINCT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 AND `employee` = '{user}'""".format(user=user), as_dict=True)
		if len(ts) > 0:
			ts = frappe.get_doc("Timesheet", ts[0].name)
		else:
			ts = frappe.get_doc({
				"doctype": "Timesheet",
				"employee": user
			})
			insert_first = True
			
	time = str(time.split(":")[0]) + ":" + str(time.split(":")[1]) + ":00"
	start = nowdate() + " " + str(time)
	row = {}
	row["activity_type"] = typ #'Execution'
	row["hours"] = 0.000
	row["from_time"] = get_datetime(get_datetime_str(start))
	row["to_time"] = get_datetime(get_datetime_str(start))
	ts.append('time_logs', row)
	if insert_first:
		ts.insert(ignore_permissions=True)
	else:
		ts.save(ignore_permissions=True)
	return 'ok'
		
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
	self.update_cost()
	self.calculate_total_amounts()
	self.calculate_percentage_billed()
	self.set_dates()
	
def auto_ts_submit():
	#************************************************************************************
	#overwrite the time_log overlap validation of timesheet and the on_submit validation
	overwrite_ts_validation()
	overwrite_ts_on_submit()
	#************************************************************************************
	
	today = nowdate() + " 00:00:00"
	midnight = get_datetime(get_datetime_str(today))
	ts_list = frappe.db.sql("""SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 AND `start_date` < '{nowdate}'""".format(nowdate=nowdate()), as_dict=True)
	for _ts in ts_list:
		ts = frappe.get_doc("Timesheet", _ts.name)
		ts.submit(ignore_permissions=True)
	