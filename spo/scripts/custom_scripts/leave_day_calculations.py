# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import nowdate, getdate
from frappe import _

@frappe.whitelist()
def get_leaves_taken(employee, leave_type):
	#leave_type = 'Urlaub' oder 'Persönlich'
	now = nowdate()
	first_of_year = getdate().strftime('%Y') + "-01-01"
	leaves_taken_query = """SELECT SUM(`total_leave_days`)
							FROM `tabLeave Application`
							WHERE `employee` = '{employee}'
							AND `leave_type` = '{leave_type}'
							AND `status` = 'Approved'
							AND `to_date` <= '{now}'
							AND `from_date` >= '{first_of_year}'""".format(employee=employee, leave_type=leave_type, now=now, first_of_year=first_of_year)
	return frappe.db.sql(leaves_taken_query, as_list=True)[0][0]