# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from spo.utils.timesheet_handlings import handle_timesheet, get_total_ts_time

class Mandat(Document):
	def validate(self):
		if self.is_new() != True:
			if not self.default_ts:
				# create start ts buchung
				handle_timesheet(frappe.session.user, self.doctype, self.name, 0)
				self.default_ts = 1
			if float(self.timer or 0) != float(get_total_ts_time(self.doctype, self.name) or 0):
				self.timer = float(get_total_ts_time(self.doctype, self.name) or 0)

	
@frappe.whitelist()
def get_dashboard_data(mitglied='', anfrage='', mandat=''):
	# Zeitbalken
	callcenter_limit = frappe.get_single("Einstellungen").limite_mandat_time
	callcenter_verwendet = 0.000
	
	if not mitglied:
		# zeit aus anfrage & mandat
		callcenter_verwendet = float(frappe.db.sql("""SELECT SUM(`hours`) FROM `tabTimesheet Detail` WHERE ((`spo_dokument` = 'Anfrage' AND `spo_referenz` = '{anfrage}') OR (`spo_dokument` = 'Mandat' AND `spo_referenz` = '{mandat}')) AND `parent` IN (
										SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 OR `docstatus` = 1)""".format(anfrage=anfrage, mandat=mandat), as_list=True)[0][0])
		callcenter_verwendet = callcenter_verwendet * 60
	else:
		# zeit aus anfrage & mandat zu mitglied
		callcenter_verwendet = float(frappe.db.sql("""SELECT SUM(`hours`)
														FROM `tabTimesheet Detail`
														WHERE
														`parent` IN (SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 OR `docstatus` = 1)
														AND 
														(`spo_dokument` = 'Anfrage' AND `spo_referenz` IN (SELECT `name` FROM `tabAnfrage` WHERE `mitglied` = 'CUST-2019-000015'))
														OR (`spo_dokument` = 'Mandat' AND `spo_referenz` IN (SELECT `name` FROM `tabMandat` WHERE `mitglied` = 'CUST-2019-000015'))""".format(anfrage=anfrage, mitglied=mitglied), as_list=True)[0][0])
		callcenter_verwendet = callcenter_verwendet * 60
		
	return {
			"callcenter_limit": callcenter_limit,
			"callcenter_verwendet": callcenter_verwendet
		}