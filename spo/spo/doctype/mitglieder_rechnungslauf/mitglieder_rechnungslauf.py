# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, os, json
from frappe.model.document import Document
from frappe.utils.data import add_days, today, add_years
from spo.spo.doctype.mitgliedschaft.mitgliedschaft import create_invoice
from frappe.utils.background_jobs import enqueue
#from frappe.utils.print_format import download_multi_pdf
from PyPDF2 import PdfFileWriter
import math
from frappe import _

class MitgliederRechnungslauf(Document):
	def before_save(self):
		vorlauf = frappe.get_doc("Einstellungen").rechnungslauf_vorlauf
		datum_inkl_vorlauf = add_days(self.datum, vorlauf)
		ablaufende_mitgliedschaften = frappe.db.sql("""SELECT `name`, `customer`, `mitgliedschafts_typ`, `ende` FROM `tabMitgliedschaft` WHERE `ende` <= '{datum_inkl_vorlauf}'
														AND `not_renew` = 0
														AND `name` NOT IN (SELECT `mitgliedschaft` FROM `tabAuslaufende Mitgliedschaften`) LIMIT 500""".format(datum_inkl_vorlauf=datum_inkl_vorlauf), as_dict=True)
		for mitglied in ablaufende_mitgliedschaften:
			row = self.append('auslaufende_mitgliedschaften', {})
			row.mitgliedschaft = mitglied.name
			row.kunde = mitglied.customer
			row.type = mitglied.mitgliedschafts_typ
			row.ende = mitglied.ende
			
	def before_submit(self):
		if len(self.auslaufende_mitgliedschaften) > 0:
			#start background job...
			max_time = 4800
			args = {
				'self': self
			}
			enqueue("spo.spo.doctype.mitglieder_rechnungslauf.mitglieder_rechnungslauf.background_rechnungslauf", queue='long', job_name='Mitglieder Rechnungslauf', timeout=max_time, **args)
		else:
			frappe.throw(_("Es sind keine auslaufende Mitgliedschaften vorhanden."))
			
def autom_rechnungslauf():
	vorlauf = frappe.get_doc("Einstellungen").rechnungslauf_vorlauf
	datum_inkl_vorlauf = add_days(today(), vorlauf)
	ablaufende_mitgliedschaften = frappe.db.sql("""SELECT `name`, `customer`, `mitgliedschafts_typ`, `ende` FROM `tabMitgliedschaft` WHERE `ende` <= '{datum_inkl_vorlauf}'
													AND `not_renew` = 0
													AND `name` NOT IN (SELECT `mitgliedschaft` FROM `tabAuslaufende Mitgliedschaften`)""".format(datum_inkl_vorlauf=datum_inkl_vorlauf), as_dict=True)
	while len(ablaufende_mitgliedschaften) > 0:
		rechnungslauf = frappe.get_doc({
			"doctype": "Mitglieder Rechnungslauf",
			"datum": today()
		})
		rechnungslauf.insert()
		ablaufende_mitgliedschaften = frappe.db.sql("""SELECT `name`, `customer`, `mitgliedschafts_typ`, `ende` FROM `tabMitgliedschaft` WHERE `ende` <= '{datum_inkl_vorlauf}'
													AND `not_renew` = 0
													AND `name` NOT IN (SELECT `mitgliedschaft` FROM `tabAuslaufende Mitgliedschaften`)""".format(datum_inkl_vorlauf=datum_inkl_vorlauf), as_dict=True)
													
def background_rechnungslauf(self):
	sinv_to_print = []
	for mitgliedschaft in self.auslaufende_mitgliedschaften:
		mitgliedschaft = frappe.get_doc("Mitgliedschaft", mitgliedschaft.mitgliedschaft)
		neue_mitgliedschaft = frappe.get_doc({
			"doctype": "Mitgliedschaft",
			"mitglied": mitgliedschaft.mitglied,
			"mitgliedschafts_typ": mitgliedschaft.mitgliedschafts_typ,
			"start": mitgliedschaft.ende,
			"ende": add_years(mitgliedschaft.ende, 1),
			"customer": mitgliedschaft.customer,
			"rechnung_an_dritte": mitgliedschaft.rechnung_an_dritte,
			"rechnungsempfaenger": mitgliedschaft.rechnungsempfaenger
		})
		neue_mitgliedschaft.insert()
		
		rechnung = create_invoice(neue_mitgliedschaft.name)
		
		neue_mitgliedschaft.rechnung = rechnung
		neue_mitgliedschaft.save()
		
		mitgliedschaft.neue_mitgliedschaft = neue_mitgliedschaft.name
		mitgliedschaft.save()
		
		if self.asap_print == 1:
			rechnung = frappe.get_doc("Sales Invoice", rechnung)
			rechnung.submit()
			sinv_to_print.append(rechnung.name)
			
	if self.asap_print == 1:
		qty = 0
		sales_invoices = []
		for sinv in sinv_to_print:
			qty += 1
			sales_invoices.append(sinv)
		if qty > 0:
			bind_source = "/assets/spo/sinvs_for_print/{rechnungslauf}/Rechnungslauf_{rechnungslauf}.pdf".format(rechnungslauf=self.name)
			physical_path = "/home/frappe/frappe-bench/sites" + bind_source
			pdf_batch(sales_invoices, format="Mitgliederrechnung", dest=str(physical_path), name=self.name)
		
		frappe.db.sql("""UPDATE `tabMitglieder Rechnungslauf` SET `rechnungen_erstellt` = 1 WHERE `name` = '{name}'""".format(name=self.name), as_list=True)
	
def pdf_batch(sales_invoices, format=None, dest=None, name=''):
	last = True
	#start background job...
	max_time = 4800
	args = {
		'sales_invoices': sales_invoices,
		'format': "Mitgliederrechnung",
		'dest': dest,
		'last': last,
		'name': name
	}
	enqueue("spo.spo.doctype.mitglieder_rechnungslauf.mitglieder_rechnungslauf.print_bind", queue='long', job_name='Erstelle PDF', timeout=max_time, **args)
	#print_bind(sinv_to_print, format="Standard", dest=str(physical_path))
	
def print_bind(sales_invoices, format=None, dest=None, last=False, name=''):
	# Concatenating pdf files
	output = PdfFileWriter()
	for sales_invoice in sales_invoices:
		output = frappe.get_print("Sales Invoice", sales_invoice, format, as_pdf = True, output = output)
		print("append to output")
	if dest != None:
		if isinstance(dest, str): # when dest is a file path
			destdir = os.path.dirname(dest)
			if destdir != '' and not os.path.isdir(destdir):
				os.makedirs(destdir)
			with open(dest, "wb") as w:
				output.write(w)
		else: # when dest is io.IOBase
			output.write(dest)
			print("first return")
		if last:
			frappe.db.sql("""UPDATE `tabMitglieder Rechnungslauf` SET `pdf_erstellt` = 1 WHERE `name` = '{name}'""".format(name=name), as_list=True)
		return
	else:
		print("second return")
		return output