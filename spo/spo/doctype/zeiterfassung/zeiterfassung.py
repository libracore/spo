# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import nowdate, add_to_date, get_datetime, get_datetime_str, time_diff_in_hours, get_time
from frappe.model.document import Document
import json
from erpnext.projects.doctype.timesheet.timesheet import Timesheet

class Zeiterfassung(Document):
	def validate(self):
		frappe.throw("Dieses Dokument können Sie nicht speichern.<br>Bitte benutzen Sie die untenstehenden Schaltflächen.", "Kann nicht gepeichert werden")
		

@frappe.whitelist()
def get_visual_overview(ts):
	ts = frappe.get_doc("Timesheet", ts)
	html_to_return = '<div class="row"><div class="col-sm-12"><div id="chart"></div></div>'
	total_arbeitszeit = 0
	total_beratnugszeit = 0
	total_mandatszeit = 0
	total_diverses = 0
	
	#arbeitszeit
	html_to_return += '<div class="col-sm-4"><h2>Präsenzzeit</h2>'
	for log in ts.time_logs:
		if log.activity_type == 'Arbeitszeit':
			html_to_return += 'Von: ' + get_time(log.from_time).strftime("%H:%M:%S") + ' bis: ' + get_time(log.to_time).strftime("%H:%M:%S") + ' Total: ' + str(log.hours) + 'h'
			total_arbeitszeit += log.hours
	html_to_return += '<h2>Pausen</h2>'
	for log in ts.time_logs:
		if log.activity_type == 'Pause':
			html_to_return += get_time(log.from_time).strftime("%H:%M:%S") + ': ' + str(log.hours) + 'h<br>'
			total_arbeitszeit -= log.hours
	html_to_return += '</div>'
	#/arbeitszeit
	
	#Mandate/Anfrage
	html_to_return += '<div class="col-sm-4"><h2>Beratungen / Mandate</h2>'
	for log in ts.time_logs:
		if log.activity_type == 'Beratung':
			html_to_return += 'Beratung (' + log.spo_referenz + '): ' + str(log.hours) + 'h<br>'
			total_beratnugszeit += log.hours
		if log.activity_type == 'Mandatsarbeit':
			html_to_return += 'Mandatsarbeit (' + log.spo_referenz + '): ' + str(log.hours) + 'h<br>'
			total_mandatszeit += log.hours
	html_to_return += '</div>'
	#/Mandate/Anfrage
	
	#diverses
	html_to_return += '<div class="col-sm-4"><h2>Diverses</h2>'
	for log in ts.time_logs:
		if log.activity_type != 'Beratung' and log.activity_type != 'Mandatsarbeit' and log.activity_type != 'Pause' and log.activity_type != 'Arbeitszeit':
			html_to_return += log.activity_type + ': ' + str(log.hours) + 'h<br>'
			total_diverses += log.hours
	html_to_return += '</div>'
	#/diverses
	
	html_to_return += '</div>'
	
	return {
			'html': html_to_return,
			'docstatus': ts.docstatus,
			'arbeitszeit': total_arbeitszeit,
			'total_beratungszeit': total_beratnugszeit,
			'total_mandatszeit': total_mandatszeit,
			'total_diverses': total_diverses
		}
	
@frappe.whitelist()
def fetch_pausen_von_ts(ts):
	ts = frappe.get_doc("Timesheet", ts)
	total_arbeitszeit = 0
	total_pausenzeit = 0
	start = ''
	ende = ''
	pausen = []
	
	#arbeitszeit & pause
	for log in ts.time_logs:
		if log.activity_type == 'Arbeitszeit':
			start = get_time(log.from_time).strftime("%H:%M:%S")
			ende = get_time(log.to_time).strftime("%H:%M:%S")
			total_arbeitszeit += log.hours
		if log.activity_type == 'Pause':
			pause = {}
			pause["start"] = get_time(log.from_time).strftime("%H:%M:%S")
			pause["dauer"] = log.hours
			pause["referenz"] = log.name
			pausen.append(pause)
			total_pausenzeit += log.hours
			total_arbeitszeit -= log.hours
	#/arbeitszeit & pause
	
	return {
			'total_arbeitszeit': total_arbeitszeit,
			'total_pausenzeit': total_pausenzeit,
			'start': start,
			'ende': ende,
			'pausen': pausen
		}

@frappe.whitelist()
def fetch_beratungs_und_mandats_arbeiten_von_ts(ts):
	ts = frappe.get_doc("Timesheet", ts)
	total_beratung = 0
	total_mandatsarbeit = 0
	beratungen = []
	
	#Beratung & Mandatsarbeiten
	for log in ts.time_logs:
		#Beratung
		if log.activity_type == 'Beratung':
			total_beratung += log.hours
			beratung = {}
			beratung["spo_referenz"] = log.spo_referenz
			beratung["dauer"] = log.hours
			beratung["referenz"] = log.name
			beratung["spo_dokument"] = log.spo_dokument
			beratung["beratung"] = 1
			beratung["mandat"] = 0
			beratungen.append(beratung)
		#/Beratung
		#Mandatsarbeiten
		if log.activity_type == 'Mandatsarbeit':
			beratung = {}
			beratung["spo_referenz"] = log.spo_referenz
			beratung["dauer"] = log.hours
			beratung["referenz"] = log.name
			beratung["spo_dokument"] = log.spo_dokument
			beratung["mandat"] = 1
			beratung["beratung"] = 0
			beratungen.append(beratung)
			total_mandatsarbeit += log.hours
		#/Mandatsarbeiten
	#/Beratung & Mandatsarbeiten
	
	return {
			'total_beratung': total_beratung,
			'total_mandatsarbeit': total_mandatsarbeit,
			'beratungen': beratungen
		}
		
@frappe.whitelist()
def fetch_diverses_von_ts(ts):
	ts = frappe.get_doc("Timesheet", ts)
	total_diverses = 0
	diverses = []
	
	#Diverses
	for log in ts.time_logs:
		if log.activity_type != 'Beratung' and log.activity_type != 'Mandatsarbeit' and log.activity_type != 'Pause' and log.activity_type != 'Arbeitszeit':
			total_diverses += log.hours
			_diverses = {}
			_diverses["dauer"] = log.hours
			_diverses["referenz"] = log.name
			_diverses["activity_type"] = log.activity_type
			diverses.append(_diverses)
	#Diverses
	
	return {
			'total_diverses': total_diverses,
			'diverses': diverses
		}
		
@frappe.whitelist()
def update_ts(ts, datum, start, ende, pausen, beratungen_mandate, diverses, working_hours):
	#**********************************************************
	#overwrite the time_log overlap validation of timesheet
	overwrite_ts_validation()
	#**********************************************************
	
	ts = frappe.get_doc("Timesheet", ts)
	ts.twh = working_hours
	ts.time_logs = []
	_datum = datum
	
	#Arbeitszeit
	start_datum = _datum + " " + start
	end_datum = _datum + " " + ende
	row = {}
	row["activity_type"] = 'Arbeitszeit'
	row["hours"] = time_diff_in_hours(get_datetime(get_datetime_str(end_datum)), get_datetime(get_datetime_str(start_datum)))
	row["from_time"] = get_datetime(get_datetime_str(start_datum))
	row["to_time"] = get_datetime(get_datetime_str(end_datum))
	ts.append('time_logs', row)
	#/Arbeitszeit
	#Pausen
	pausen = json.loads(pausen)
	for pause in pausen:
		datum = _datum + " " + pause["from"]
		row = {}
		row["activity_type"] = 'Pause'
		row["hours"] = pause['dauer']
		row["from_time"] = get_datetime(get_datetime_str(datum))
		ts.append('time_logs', row)
	#/Pausen
	#Beratungen/Mandate
	beratungen_mandate = json.loads(beratungen_mandate)
	datum = _datum + " 00:00:00"
	for beratung in beratungen_mandate:
		row = {}
		if beratung["mandat"] == 1:
			row["activity_type"] = 'Mandatsarbeit'
		else:
			row["activity_type"] = 'Beratung'
		row["hours"] = beratung['dauer']
		row["from_time"] = get_datetime(get_datetime_str(datum))
		row["spo_dokument"] = beratung['spo_dokument']
		row["spo_referenz"] = beratung['spo_referenz']
		ts.append('time_logs', row)
	#/Beratungen/Mandate
	#Diverses
	diverses = json.loads(diverses)
	datum = _datum + " 00:00:00"
	for div in diverses:
		row = {}
		row["activity_type"] = div["activity_type"]
		row["hours"] = div['dauer']
		row["from_time"] = get_datetime(get_datetime_str(datum))
		ts.append('time_logs', row)
	#/Diverses
	ts.save(ignore_permissions=True)
	return "ok"
	
@frappe.whitelist()
def save_ts(ma, datum, start, ende, pausen, beratungen_mandate, diverses, working_hours):
	if check_if_ts_exist(ma, datum):
		frappe.throw("Am gewählten Datum existiert für diese(n) Mitarbeiter(in) bereits ein Timesheet")
	#**********************************************************
	#overwrite the time_log overlap validation of timesheet
	overwrite_ts_validation()
	#**********************************************************
	_datum = datum
	#Arbeitszeit
	start_datum = _datum + " " + start
	end_datum = _datum + " " + ende
	ts = frappe.get_doc({
		"doctype": "Timesheet",
		"employee": ma,
		"start_date": datum,
		"end_date": datum,
		"twh": working_hours,
		"time_logs": [
			{
				"activity_type": "Arbeitszeit",
				"hours": time_diff_in_hours(get_datetime(get_datetime_str(end_datum)), get_datetime(get_datetime_str(start_datum))),
				"from_time": get_datetime(get_datetime_str(start_datum)),
				"to_time": get_datetime(get_datetime_str(end_datum))
			}
		]
	})
	ts.insert()
	#/Arbeitszeit
	#Pausen
	pausen = json.loads(pausen)
	for pause in pausen:
		datum = _datum + " " + pause["from"]
		row = {}
		row["activity_type"] = 'Pause'
		row["hours"] = pause['dauer']
		row["from_time"] = get_datetime(get_datetime_str(datum))
		ts.append('time_logs', row)
	#/Pausen
	#Beratungen/Mandate
	beratungen_mandate = json.loads(beratungen_mandate)
	datum = _datum + " 00:00:00"
	for beratung in beratungen_mandate:
		row = {}
		if beratung["mandat"] == 1:
			row["activity_type"] = 'Mandatsarbeit'
		else:
			row["activity_type"] = 'Beratung'
		row["hours"] = beratung['dauer']
		row["from_time"] = get_datetime(get_datetime_str(datum))
		row["spo_dokument"] = beratung['spo_dokument']
		row["spo_referenz"] = beratung['spo_referenz']
		ts.append('time_logs', row)
	#/Beratungen/Mandate
	#Diverses
	diverses = json.loads(diverses)
	datum = _datum + " 00:00:00"
	for div in diverses:
		row = {}
		row["activity_type"] = div["activity_type"]
		row["hours"] = div['dauer']
		row["from_time"] = get_datetime(get_datetime_str(datum))
		ts.append('time_logs', row)
	#/Diverses
	ts.save(ignore_permissions=True)
	return ts.name
	
def check_if_ts_exist(ma, datum):
	ts = frappe.db.sql("""SELECT `name` FROM `tabTimesheet` WHERE `employee` = '{ma}' AND `start_date` = '{datum}'""".format(ma=ma, datum=datum), as_dict=True)
	if len(ts) > 0:
		return True
	else:
		return False
	
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
	
@frappe.whitelist()
def get_ma_from_user(user):
	user = frappe.db.sql("""SELECT `name` FROM `tabEmployee` WHERE `user_id` = '{user}'""".format(user=user), as_list=True)
	if user:
		user = user[0][0]
	else:
		user = ''
	return user