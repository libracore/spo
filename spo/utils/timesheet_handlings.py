# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def handle_timesheet(user, doctype, reference, time):
	user = frappe.db.sql("""SELECT `name` FROM `tabEmployee` WHERE `user_id` = '{user}'""".format(user=user), as_list=True)
	time = float(time)
	if user:
		user = user[0][0]
		ts = check_if_timesheet_exist(user, doctype, reference)
		if ts:
			update_timesheet(ts, time, doctype, reference)
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
				"spo_referenz": reference
			}
		]
	})
	ts.insert()
	
def update_timesheet(ts, time, doctype, reference):
	ts = frappe.get_doc("Timesheet", ts)
	for time_log in ts.time_logs:
		if time_log.spo_dokument == doctype:
			if time_log.spo_referenz == reference:
				if time > get_default_time(doctype):
					time_log.hours = time
	ts.save()
				
def get_default_time(doctype):
	time = 0
	defaults = frappe.get_doc("Einstellungen").ts_defaults
	for default in defaults:
		if default.dokument == doctype:
			time = default.default_hours
			break
	return time