# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Mandat(Document):
	pass

	
@frappe.whitelist()
def get_dashboard_data(mitglied):
	# m_ = als mitglied
	# o_ = ohne mitgliedschaft
	
	m_last_year = frappe.db.sql("""SELECT SUM(`timer`) FROM `tabAnfrage` WHERE `mitglied` = '{mitglied}' AND `mitgliedschaft` IS NOT NULL AND YEAR(`creation`) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 YEAR))""".format(mitglied=mitglied), as_list=True)[0][0] or 0
	o_last_year = frappe.db.sql("""SELECT SUM(`timer`) FROM `tabAnfrage` WHERE `mitglied` = '{mitglied}' AND `mitgliedschaft` IS NULL AND YEAR(`creation`) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 YEAR))""".format(mitglied=mitglied), as_list=True)[0][0] or 0
	m_ytd = frappe.db.sql("""SELECT SUM(`timer`) FROM `tabAnfrage` WHERE `mitglied` = '{mitglied}' AND `mitgliedschaft` IS NOT NULL AND YEAR(`creation`) = YEAR(CURDATE()) AND DATE_FORMAT(`creation`, '%Y-%m-%d') <= CURDATE()""".format(mitglied=mitglied), as_list=True)[0][0] or 0
	o_ytd = frappe.db.sql("""SELECT SUM(`timer`) FROM `tabAnfrage` WHERE `mitglied` = '{mitglied}' AND `mitgliedschaft` IS NULL AND YEAR(`creation`) = YEAR(CURDATE()) AND DATE_FORMAT(`creation`, '%Y-%m-%d') <= CURDATE()""".format(mitglied=mitglied), as_list=True)[0][0] or 0
	m_q1 = frappe.db.sql("""SELECT SUM(`timer`) FROM `tabAnfrage` WHERE `mitglied` = '{mitglied}' AND `mitgliedschaft` IS NOT NULL AND QUARTER(`creation`) = 1 AND YEAR(`creation`) = YEAR(CURDATE())""".format(mitglied=mitglied), as_list=True)[0][0] or 0
	o_q1 = frappe.db.sql("""SELECT SUM(`timer`) FROM `tabAnfrage` WHERE `mitglied` = '{mitglied}' AND `mitgliedschaft` IS NULL AND QUARTER(`creation`) = 1 AND YEAR(`creation`) = YEAR(CURDATE())""".format(mitglied=mitglied), as_list=True)[0][0] or 0
	m_q2 = frappe.db.sql("""SELECT SUM(`timer`) FROM `tabAnfrage` WHERE `mitglied` = '{mitglied}' AND `mitgliedschaft` IS NOT NULL AND QUARTER(`creation`) = 2 AND YEAR(`creation`) = YEAR(CURDATE())""".format(mitglied=mitglied), as_list=True)[0][0] or 0
	o_q2 = frappe.db.sql("""SELECT SUM(`timer`) FROM `tabAnfrage` WHERE `mitglied` = '{mitglied}' AND `mitgliedschaft` IS NULL AND QUARTER(`creation`) = 2 AND YEAR(`creation`) = YEAR(CURDATE())""".format(mitglied=mitglied), as_list=True)[0][0] or 0
	m_q3 = frappe.db.sql("""SELECT SUM(`timer`) FROM `tabAnfrage` WHERE `mitglied` = '{mitglied}' AND `mitgliedschaft` IS NOT NULL AND QUARTER(`creation`) = 3 AND YEAR(`creation`) = YEAR(CURDATE())""".format(mitglied=mitglied), as_list=True)[0][0] or 0
	o_q3 = frappe.db.sql("""SELECT SUM(`timer`) FROM `tabAnfrage` WHERE `mitglied` = '{mitglied}' AND `mitgliedschaft` IS NULL AND QUARTER(`creation`) = 3 AND YEAR(`creation`) = YEAR(CURDATE())""".format(mitglied=mitglied), as_list=True)[0][0] or 0
	m_q4 = frappe.db.sql("""SELECT SUM(`timer`) FROM `tabAnfrage` WHERE `mitglied` = '{mitglied}' AND `mitgliedschaft` IS NOT NULL AND QUARTER(`creation`) = 4 AND YEAR(`creation`) = YEAR(CURDATE())""".format(mitglied=mitglied), as_list=True)[0][0] or 0
	o_q4 = frappe.db.sql("""SELECT SUM(`timer`) FROM `tabAnfrage` WHERE `mitglied` = '{mitglied}' AND `mitgliedschaft` IS NULL AND QUARTER(`creation`) = 4 AND YEAR(`creation`) = YEAR(CURDATE())""".format(mitglied=mitglied), as_list=True)[0][0] or 0
	
	callcenter_limit = frappe.get_single("Einstellungen").limite_mandat_time
	anfragen = frappe.get_list("Anfrage", [["mitglied", "=", mitglied]])
	callcenter_verwendet = 0
	for anfrage in anfragen:
		callcenter_verwendet += frappe.get_doc("Anfrage", anfrage).timer
		# zeiten von mandat muss noch addiert werden!
	
	return {
			"m_last_year": m_last_year,
			"o_last_year": o_last_year,
			"m_ytd": m_ytd,
			"o_ytd": o_ytd,
			"m_q1": m_q1,
			"o_q1": o_q1,
			"m_q2": m_q2,
			"o_q2": o_q2,
			"m_q3": m_q3,
			"o_q3": o_q3,
			"m_q4": m_q4,
			"o_q4": o_q4,
			"callcenter_limit": callcenter_limit,
			"callcenter_verwendet": callcenter_verwendet
			}