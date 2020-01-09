# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from spo.utils.timesheet_handlings import handle_timesheet, get_total_ts_time, get_zeiten_uebersicht
from frappe.utils.data import today, add_days, nowdate, get_datetime_str

class Mandat(Document):
	def validate(self):
		if self.is_new() != True:
			if not self.default_ts:
				# create start ts buchung
				default_time = get_default_time("Mandat")
				handle_timesheet(frappe.session.user, self.doctype, self.name, default_time, '', nowdate())
				self.default_ts = 1

	def onload(self):
		if self.is_new() != True:
			if float(self.timer or 0) != float(get_total_ts_time(self.doctype, self.name) or 0):
				self.timer = float(get_total_ts_time(self.doctype, self.name) or 0)
	
def get_default_time(doctype):
	time = 0
	defaults = frappe.get_doc("Einstellungen").ts_defaults
	for default in defaults:
		if default.dokument == doctype:
			time = default.default_hours
			break
	return time
	
@frappe.whitelist()
def get_dashboard_data(mitglied='', anfrage='', mandat=''):
	# Zeitbalken
	callcenter_limit = frappe.get_single("Einstellungen").limite_mandat_time
	callcenter_verwendet = 0.000
	
	if not mitglied:
		# zeit aus anfrage & mandat
		try:
			callcenter_verwendet = float(frappe.db.sql("""SELECT SUM(`hours`) FROM `tabTimesheet Detail` WHERE (
														(`spo_dokument` = 'Anfrage' AND `spo_referenz` = '{anfrage}')
														OR (`spo_dokument` = 'Mandat' AND `spo_referenz` = '{mandat}')
														OR (`spo_dokument` = 'Anforderung Patientendossier' AND `spo_referenz` IN (
															SELECT `name`FROM `tabAnforderung Patientendossier` WHERE `mandat` = '{mandat}' AND `docstatus` != 2))
														OR (`spo_dokument` = 'Medizinischer Bericht' AND `spo_referenz` IN (
															SELECT `name`FROM `tabMedizinischer Bericht` WHERE `mandat` = '{mandat}' AND `docstatus` != 2))
														OR (`spo_dokument` = 'Triage' AND `spo_referenz` IN (
															SELECT `name`FROM `tabTriage` WHERE `mandat` = '{mandat}' AND `docstatus` != 2))
														OR (`spo_dokument` = 'Vollmacht' AND `spo_referenz` IN (
															SELECT `name`FROM `tabVollmacht` WHERE `mandat` = '{mandat}' AND `docstatus` != 2))
														OR (`spo_dokument` = 'Abschlussbericht' AND `spo_referenz` IN (
															SELECT `name`FROM `tabAbschlussbericht` WHERE `mandat` = '{mandat}' AND `docstatus` != 2))
														) AND `parent` IN (
															SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 OR `docstatus` = 1)""".format(anfrage=anfrage, mandat=mandat), as_list=True)[0][0])
		except:
			callcenter_verwendet = 0
		callcenter_verwendet = callcenter_verwendet * 60
	else:
		# zeit aus anfrage & mandat zu mitglied
		try:
			callcenter_verwendet = float(frappe.db.sql("""SELECT SUM(`hours`)
														FROM `tabTimesheet Detail`
														WHERE
														`parent` IN (SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 OR `docstatus` = 1)
														AND (
														(`spo_dokument` = 'Anfrage' AND `spo_referenz` IN (
															SELECT `name` FROM `tabAnfrage` WHERE `mitglied` = '{mitglied}'))
														OR (`spo_dokument` = 'Mandat' AND `spo_referenz` = '{mandat}')
														OR (`spo_dokument` = 'Anforderung Patientendossier' AND `spo_referenz` IN (
															SELECT `name`FROM `tabAnforderung Patientendossier` WHERE `mandat` = '{mandat}' AND `docstatus` != 2))
														OR (`spo_dokument` = 'Medizinischer Bericht' AND `spo_referenz` IN (
															SELECT `name`FROM `tabMedizinischer Bericht` WHERE `mandat` = '{mandat}' AND `docstatus` != 2))
														OR (`spo_dokument` = 'Triage' AND `spo_referenz` IN (
															SELECT `name`FROM `tabTriage` WHERE `mandat` = '{mandat}' AND `docstatus` != 2))
														OR (`spo_dokument` = 'Vollmacht' AND `spo_referenz` IN (
															SELECT `name`FROM `tabVollmacht` WHERE `mandat` = '{mandat}' AND `docstatus` != 2))
														OR (`spo_dokument` = 'Abschlussbericht' AND `spo_referenz` IN (
															SELECT `name`FROM `tabAbschlussbericht` WHERE `mandat` = '{mandat}' AND `docstatus` != 2))
														)""".format(anfrage=anfrage, mitglied=mitglied, mandat=mandat), as_list=True)[0][0])
		except:
			callcenter_verwendet = 0
		callcenter_verwendet = callcenter_verwendet * 60
		
	return {
			"callcenter_limit": callcenter_limit,
			"callcenter_verwendet": callcenter_verwendet
		}
		
@frappe.whitelist()
def create_zeiten_uebersicht(dt, name):
	alle_zeiten = get_zeiten_uebersicht(dt, name)
	if alle_zeiten:
		html = '<div style="width: 100%;"><table style="width: 100%;" class="table-striped"><tr><th>Datum</th><th>Dokument</th><th>Arbeit</th><th>Stunden</th><th>Timesheet</th><th>Bearbeiten</th></tr>'
		for zeit in alle_zeiten:
			if not zeit.spo_remark:
				zeit.spo_remark = ''
			html += '<tr><td>' + get_datetime_str(zeit.from_time).split(" ")[0] + '</td><td>' + zeit.spo_dokument + ' (' + zeit.spo_referenz + ')</td><td>' + str(zeit.spo_remark) + '</td><td>' + str(zeit.hours) + '</td><td>' + zeit.parent + '</td><td><a data-referenz="' + zeit.parent + '" data-funktion="open_ts"><i class="fa fa-edit"></i></a></td></tr>'
		html += '</table></div>'
		return html
	else:
		return False