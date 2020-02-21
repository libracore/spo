# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import getdate, add_days

def execute(filters=None):
	columns, data = ["Mitarbeiter:Link/Employee:200", "Name:Data:200"], []
	employee_filter = ''
	if filters.employee:
		employee_filter = """ AND `name` = '{employee}'""".format(employee=filters.employee)
		
	employees = frappe.db.sql("""SELECT `name`, `employee_name`, `anstellungsgrad` FROM `tabEmployee` WHERE `status` = 'Active'{employee_filter}""".format(employee_filter=employee_filter), as_dict=True)
	activity_types = frappe.db.sql("""SELECT `name` FROM `tabActivity Type` ORDER BY `name` ASC""", as_dict=True)
	for act_type in activity_types:
		columns.append(act_type.name + ":Float:50")
		
	#Feiertage
	ganze_feiertage = frappe.db.sql("""SELECT COUNT(`name`) FROM `tabHoliday` WHERE `half_day` = 0 AND `holiday_date` BETWEEN '{von}' AND '{bis}'""".format(von=filters.from_date, bis=filters.to_date), as_list=True)
	if ganze_feiertage[0][0]:
		ganze_feiertage = ganze_feiertage[0][0]
	else:
		ganze_feiertage = 0
		
	halbe_feiertage = frappe.db.sql("""SELECT COUNT(`name`) FROM `tabHoliday` WHERE `half_day` = 1 AND `holiday_date` BETWEEN '{von}' AND '{bis}'""".format(von=filters.from_date, bis=filters.to_date), as_list=True)
	if halbe_feiertage[0][0]:
		halbe_feiertage = halbe_feiertage[0][0] / 2
	else:
		halbe_feiertage = 0
		
	feiertage = ganze_feiertage + halbe_feiertage
	
	#Allgemeine Sollzeit
	von = getdate(filters.from_date)
	bis = getdate(filters.to_date)
	sollzeit = 0
	
	while von <= bis:
		if von.weekday() < 5:
			sollzeit += 8.4
		von = add_days(von, 1)
		
	sollzeit = sollzeit - (feiertage * 8.4)
	
	for employee in employees:
		data_to_append = []
		data_to_append.append(employee.name)
		data_to_append.append(employee.employee_name)
		total_arbeitszeit = 0
		total_rueckmeldungen = 0
		
		for act_type in activity_types:
			time_logs = frappe.db.sql("""SELECT SUM(`hours`) FROM `tabTimesheet Detail` WHERE `activity_type` = '{act_type}' AND DATE(`from_time`) >= '{von}' AND DATE(`from_time`) <= '{bis}' AND `parent` IN (
											SELECT `name` FROM `tabTimesheet` WHERE `employee` = '{employee}' AND `docstatus` != 2)""".format(von=filters.from_date, bis=filters.to_date, act_type=act_type.name, employee=employee.name), as_list=True)
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
		data_to_append.append(feiertage)
		urlaub = frappe.db.sql("""SELECT SUM(`total_leave_days`) FROM `tabLeave Application` WHERE `employee` = '{employee}' AND `status` = 'Approved' AND `docstatus` = 1 AND `from_date` BETWEEN '{von}' AND '{bis}'""".format(employee=employee.name, von=filters.from_date, bis=filters.to_date), as_list=True)
		if urlaub[0][0]:
			urlaub = urlaub[0][0]
		else:
			urlaub = 0
		data_to_append.append(urlaub)
		_sollzeit = (sollzeit / 100) * employee.anstellungsgrad
		_sollzeit = _sollzeit - (urlaub * 8.4)
		data_to_append.append(_sollzeit)
		data.append(data_to_append)
		
	columns.append("Summe Arbeitszeit:Float")
	columns.append("Summe Rückmeldungen:Float")
	columns.append("Feiertage:Float")
	columns.append("Bezogener Urlaub:Float")
	columns.append("Sollzeit:Float")
	return columns, data
