# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def handle_timesheet(user, doctype, reference):
	if check_if_timesheet_exist(user, doctype, reference):
		update_timesheet(user, doctype, reference, time)
	else:
		create_timesheet(user, doctype, reference, time)
	
def check_if_timesheet_exist(user, doctype, reference):
	return
	
def create_timesheet(user, doctype, reference, time):
	return
	
def update_timesheet(user, doctype, reference, time):
	return