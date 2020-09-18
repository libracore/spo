# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import getdate, add_days
from erpnext.hr.doctype.leave_application.leave_application import get_leave_details

def execute(filters=None):
	columns, data = ["Mitarbeiter:Link/Employee:200", "Name:Data:200"], []
	employee_filter = ''
	if filters.employee:
		employee_filter = """ AND `name` = '{employee}'""".format(employee=filters.employee)
		
	employees = frappe.db.sql("""SELECT `name`, `employee_name`, `anstellungsgrad`, `company`, `holiday_list`, `anstellung`, `date_of_joining` FROM `tabEmployee` WHERE `status` = 'Active'{employee_filter}""".format(employee_filter=employee_filter), as_dict=True)
	activity_types = frappe.db.sql("""SELECT `name` FROM `tabActivity Type` ORDER BY `name` ASC""", as_dict=True)
	for act_type in activity_types:
		columns.append(act_type.name + ":Float:50")

	#Allgemeine Sollzeit
	von = getdate(filters.from_date)
	bis = getdate(filters.to_date)
	sollzeit = 0
	
	while von <= bis:
		if von.weekday() < 5:
			sollzeit += 8.4
		von = add_days(von, 1)
		
	'''	
		Sollzeitberechnung (gem. DaTa):
		x = ((Anzahl Mo - Fr) * Tagesarbeitszeit) - ((Anzahl Feiertage) * Tagesarbeitszeit)
		y = x * (Anstellungsgrad in %)
		z = y - ((Anzahl Urlaubstage) * Tagesarbeitszeit)
		Sollzeit = z (--> sollzeit)
	'''
	
	for employee in employees:
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
		emp_soll = sollzeit # --> Allgemeine Sollzeit
		if employee.date_of_joining > getdate(filters.from_date):
			#Emp spezifische Sollzeit
			von = getdate(employee.date_of_joining)
			bis = getdate(filters.to_date)
			emp_soll = 0
			while von <= bis:
				if von.weekday() < 5:
					emp_soll += 8.4
				von = add_days(von, 1)
		
		# Timelogs:
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
		
		# Feiertage:
		# wenn employee nicht stundenlohn:
		if employee.anstellung != 'Stundenlohn':
			default_holiday_list = frappe.get_doc("Company", employee.company).default_holiday_list
			if employee.holiday_list:
				default_holiday_list = employee.holiday_list

			ganze_feiertage = frappe.db.sql("""SELECT COUNT(`name`) FROM `tabHoliday` WHERE `half_day` = 0 AND `holiday_date` BETWEEN '{von}' AND '{bis}' AND `parent` = '{default_holiday_list}' AND `percentage_sick` = 0""".format(von=filters.from_date, bis=filters.to_date, default_holiday_list=default_holiday_list), as_list=True)
			if ganze_feiertage[0][0]:
				ganze_feiertage = ganze_feiertage[0][0]
			else:
				ganze_feiertage = 0
				
			halbe_feiertage = frappe.db.sql("""SELECT COUNT(`name`) FROM `tabHoliday` WHERE `half_day` = 1 AND `holiday_date` BETWEEN '{von}' AND '{bis}' AND `parent` = '{default_holiday_list}' AND `percentage_sick` = 0""".format(von=filters.from_date, bis=filters.to_date, default_holiday_list=default_holiday_list), as_list=True)
			if halbe_feiertage[0][0]:
				halbe_feiertage = halbe_feiertage[0][0] / 2
			else:
				halbe_feiertage = 0
				
			prozentuale_feiertage = frappe.db.sql("""SELECT SUM(`sick_percentage`) FROM `tabHoliday` WHERE `holiday_date` BETWEEN '{von}' AND '{bis}' AND `parent` = '{default_holiday_list}' AND `percentage_sick` = 1""".format(von=filters.from_date, bis=filters.to_date, default_holiday_list=default_holiday_list), as_list=True)
			if prozentuale_feiertage[0][0]:
				prozentuale_feiertage = ((8.4 / 100) * prozentuale_feiertage[0][0]) / 8.4
			else:
				prozentuale_feiertage = 0
				
			feiertage = ganze_feiertage + halbe_feiertage + prozentuale_feiertage
			data_to_append.append(feiertage)
		
		
			# Urlaub:
			urlaub = frappe.db.sql("""SELECT SUM(`total_leave_days`) FROM `tabLeave Application` WHERE `employee` = '{employee}' AND `status` = 'Approved' AND `docstatus` = 1 AND `from_date` BETWEEN '{von}' AND '{bis}'""".format(employee=employee.name, von=filters.from_date, bis=filters.to_date), as_list=True)
			if urlaub[0][0]:
				urlaub = urlaub[0][0]
			else:
				urlaub = 0
			data_to_append.append(urlaub)
			data_to_append.append(urlaub_total)
			
			# Sollzeit:
			_sollzeit = emp_soll - (feiertage * 8.4)
			_sollzeit = (_sollzeit / 100) * employee.anstellungsgrad
			_sollzeit = _sollzeit - (urlaub * 8.4)
			data_to_append.append(_sollzeit)
			
			#übertrag aus vorjahr
			uebertrag = 0
			uebertraege = frappe.db.sql("""SELECT `uebertrag_auf_jahr`, `stunden` FROM `tabVorjahressaldo` WHERE `parent` = '{employee}'""".format(employee=employee.name), as_dict=True)
			for _uebertrag in uebertraege:
				if getdate(filters.from_date).strftime("%Y") == _uebertrag["uebertrag_auf_jahr"]:
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
				if getdate(filters.from_date).strftime("%Y") == _uebertrag["uebertrag_auf_jahr"]:
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
