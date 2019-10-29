# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import nowdate, add_to_date

@frappe.whitelist()
def handle_timesheet(user, doctype, reference, time):
	user = frappe.db.sql("""SELECT `name` FROM `tabEmployee` WHERE `user_id` = '{user}'""".format(user=user), as_list=True)
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
	ts = frappe.db.sql("""SELECT DISTINCT `parent` FROM `tabTimesheet Detail` WHERE `spo_dokument` = '{doctype}' AND `spo_referenz` = '{reference}' AND `parent` IN (
							SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 AND `employee` = '{user}')""".format(user=user, doctype=doctype, reference=reference), as_dict=True)
	if len(ts) > 0:
		return ts[0].parent
	else:
		return False
	
def create_timesheet(user, doctype, reference, time):
	default_time = get_default_time(doctype)
	if time < default_time:
		time = default_time
	ts = frappe.get_doc({
		"doctype": "Timesheet",
		"employee": user,
		"time_logs": [
			{
				"activity_type": "Execution",
				"hours": time,
				"spo_dokument": doctype,
				"spo_referenz": reference,
				"from_time": add_to_date(nowdate(), days=100)
			}
		]
	})
	ts.insert()
	cleanup_ts(user)
	
def update_timesheet(ts, time, doctype, reference, user):
	ts = frappe.get_doc("Timesheet", ts)
	if len(ts.time_logs) <= 1:
		for time_log in ts.time_logs:
			if time_log.spo_dokument == doctype:
				if time_log.spo_referenz == reference:
					if time > get_default_time(doctype):
						time_log.hours = time
	else:
		found = False
		for time_log in ts.time_logs:
			if not found:
				if time_log.spo_dokument == doctype:
					if time_log.spo_referenz == reference:
						if time > get_default_time(doctype):
							time_log.hours = time
							found = True
							start = add_to_date(time_log.to_time, hours=0.001)
			else:
				time_log.from_time = start
				time_log.to_time = add_to_date(start, hours=time_log.hours)
				start = add_to_date(time_log.to_time, hours=0.001)
	ts.save()
	cleanup_ts(user)
				
def get_default_time(doctype):
	time = 0
	defaults = frappe.get_doc("Einstellungen").ts_defaults
	for default in defaults:
		if default.dokument == doctype:
			time = default.default_hours
			break
	return time
	
def cleanup_ts(user):
	all_ts = frappe.db.sql("""SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 AND `employee` = '{user}'""".format(user=user), as_dict=True)
	all_time_logs = []
	for _ts in all_ts:
		ts = frappe.get_doc("Timesheet", _ts.name)
		for time_log in ts.time_logs:
			all_time_logs.append(time_log)
			
	for _ts in all_ts:
		ts = frappe.get_doc("Timesheet", _ts.name)
		ts.delete()
			
	new_ts = frappe.get_doc({
		"doctype": "Timesheet",
		"employee": user,
		"time_logs": []
	})
	start = nowdate() + " 00:00:00"
	for time_log in all_time_logs:
		time_log.from_time = start
		time_log.to_time = add_to_date(start, hours=time_log.hours)
		new_ts.time_logs.append(time_log)
		start = add_to_date(start, hours=time_log.hours + 0.001)
	new_ts.insert()
	# for _ts in all_ts:
		# ts = frappe.get_doc("Timesheet", _ts.name)
		# ts.delete()