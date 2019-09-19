# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Anfrage(Document):
	pass

@frappe.whitelist()
def get_valid_mitgliedschaft_based_on_mitgliedernummer(mitgliedernummer):
	query = """SELECT * FROM `tabMitgliedschaft` WHERE `mitglied` = '{mitgliedernummer}' AND `ende` >= CURDATE()""".format(mitgliedernummer=mitgliedernummer)
	return frappe.db.sql(query, as_dict=True)
	
@frappe.whitelist()
def get_vorschlagswerte(frm, vorname='', nachname='', strasse='', hausnummer='', ort='', plz=''):
	#Suche nach Vor- resp. Nachnamen
	name_query = ''
	if vorname and not nachname:
		name_query = "`customer_name` LIKE '%{vorname}%'".format(vorname=vorname)
	if nachname and not vorname:
		name_query = "`customer_name` LIKE '%{nachname}%'".format(nachname=nachname)
	if vorname and nachname:
		name_query = "`customer_name` LIKE '%{vorname}%{nachname}%' OR `customer_name` LIKE '%{nachname}%{vorname}%'".format(vorname=vorname, nachname=nachname)
		
	namens_matches = ''
	if name_query:
		namens_matches = frappe.db.sql("""SELECT `name` FROM `tabCustomer` WHERE {name_query}""".format(name_query=name_query), as_dict=True)
		if namens_matches:
			_namens_matches = '<h2>Namens Matche</h2>'
			for match in namens_matches:
				customer = frappe.get_doc("Customer", match.name)
				_namens_matches += '<div class="panel panel-default"><div class="panel-heading">{name}<div class="pull-right" style="margin: 0px;"><button class="btn btn-primary btn-sm primary-action" style="padding: 2px;" onclick="fetch_data_from_search({frm}, {name_for_js})"><span>Übernehmen</span></button></div></div><div class="panel-body">'.format(name=customer.customer_name, name_for_js="'" + customer.customer_name + "'", frm= "'" + frm + "'")
				address = get_address(match.name)
				_namens_matches += address.address_line1 + "<br>" + address.pincode + " " + address.city
				_namens_matches += '</div></div>'
			namens_matches = _namens_matches
	else:
		namens_matches = '<h2>Namens Matches</h2><p>Fehlende Angaben!</p>'
	
	#Suche nach Adressen
	address_query = ''
	if strasse and not hausnummer:
		address_query = "`address_line1` LIKE '%{strasse}%'".format(strasse=strasse)
	if hausnummer and not strasse:
		address_query = "`address_line1` LIKE '%{hausnummer}%'".format(hausnummer=hausnummer)
	if strasse and hausnummer:
		address_query = "(`address_line1` LIKE '%{strasse}%{hausnummer}%' OR `address_line1` LIKE '%{hausnummer}%{strasse}%')".format(strasse=strasse, hausnummer=hausnummer)
	
	if address_query:
		if ort:
			address_query += " AND `city` LIKE '%{ort}%'".format(ort=ort)
		if plz:
			address_query += " AND `pincode` LIKE '%{plz}%'".format(plz=plz)
	else:
		if ort:
			address_query = "`city` LIKE '%{ort}%'".format(ort=ort)
			if plz:
				address_query += " AND `pincode` LIKE '%{plz}%'".format(plz=plz)
		else:
			if plz:
				address_query = "`pincode` LIKE '%{plz}%'".format(plz=plz)
				
	address_matches = ''
	if address_query:
		#address_matches = frappe.db.sql("""SELECT `name` FROM `tabAddress` WHERE {address_query}""".format(address_query=address_query), as_dict=True)
		address_matches = frappe.db.sql("""SELECT `link_name` FROM `tabDynamic Link` WHERE `link_doctype` = 'Customer' AND `parent` IN (SELECT `name` FROM `tabAddress` WHERE {address_query})""".format(address_query=address_query), as_dict=True)
		if address_matches:
			_address_matches = '<h2>Adressen Matches</h2>'
			for match in address_matches:
				customer = frappe.get_doc("Customer", match.link_name)
				_address_matches += '<div class="panel panel-default"><div class="panel-heading">{name}<div class="pull-right" style="margin: 0px;"><button class="btn btn-primary btn-sm primary-action" style="padding: 2px;" onclick="fetch_data_from_search({frm}, {name_for_js})"><span>Übernehmen</span></button></div></div><div class="panel-body">'.format(name=customer.customer_name, name_for_js="'" + customer.customer_name + "'", frm= "'" + frm + "'")
				address = get_address(match.link_name)
				_address_matches += address.address_line1 + "<br>" + address.pincode + " " + address.city
				_address_matches += '</div></div>'
			address_matches = _address_matches
	else:
		address_matches = '<h2>Adress Matches</h2><p>Fehlende Angaben!</p>'
	
	#Suche nach Kombinationen von Namen und Adressen
	full_matches = ''
	if name_query and address_query:
		ref_list = """SELECT `link_name` FROM `tabDynamic Link` WHERE `link_doctype` = 'Customer' AND `parent` IN (SELECT `name` FROM `tabAddress` WHERE {address_query})""".format(address_query=address_query)
		full_matches = frappe.db.sql("""SELECT `name` FROM `tabCustomer` WHERE {name_query} AND `name` IN ({ref_list})""".format(name_query=name_query, ref_list=ref_list), as_dict=True)
		if full_matches:
			_full_matches = '<h2>Vollständige Matches</h2>'
			for match in full_matches:
				customer = frappe.get_doc("Customer", match.name)
				_full_matches += '<div class="panel panel-default"><div class="panel-heading">{name}<div class="pull-right" style="margin: 0px;"><button class="btn btn-primary btn-sm primary-action" style="padding: 2px;" onclick="fetch_data_from_search({frm}, {name_for_js})"><span>Übernehmen</span></button></div></div><div class="panel-body">'.format(name=customer.customer_name, name_for_js="'" + customer.customer_name + "'", frm= "'" + frm + "'")
				address = get_address(match.name)
				_full_matches += address.address_line1 + "<br>" + address.pincode + " " + address.city
				_full_matches += '</div></div>'
			full_matches = _full_matches
	
	#Vorbereitung return daten
	data = {}
	data['namens_matches'] = namens_matches or '<h2>Namens Matches</h2><p>Keine übereinstimmungen gefunden</p>'
	data['address_matches'] = address_matches or '<h2>Adress Matches</h2><p>Keine übereinstimmungen gefunden</p>'
	data['full_matches'] = full_matches or '<h2>Vollständige Matches</h2><p>Keine übereinstimmungen gefunden</p>'
	
	return data
	
@frappe.whitelist()
def get_address(customer):
	return frappe.db.sql("""SELECT * FROM `tabAddress` WHERE `name` = (SELECT `parent` FROM `tabDynamic Link` WHERE `link_doctype` = 'Customer' AND `parenttype` = 'Address' AND `link_name` = '{customer}' LIMIT 1)""".format(customer=customer), as_dict=True)[0]
	
@frappe.whitelist()
def update_frm_with_fetched_data(frm, name):
	anfrage = frappe.get_doc("Anfrage", frm)
	customer = frappe.get_doc("Customer", name)
	address = get_address(name)
	anfrage.vorname = customer.customer_name.split(" ")[0]
	anfrage.nachname = customer.customer_name.split(" ")[1] or ''
	anfrage.strasse = address.address_line1.split(" ")[0]
	anfrage.hausnummer = address.address_line1.split(" ")[1] or ''
	anfrage.ort = address.city
	anfrage.telefon = address.phone
	anfrage.mobile = address.fax
	anfrage.email = address.email_id
	anfrage.plz = address.pincode
	anfrage.mitglied = name
	#anfrage.mitgliedschaft = get_valid_mitgliedschaft_based_on_mitgliedernummer(name)[0].name or ''
	if get_valid_mitgliedschaft_based_on_mitgliedernummer(name):
		anfrage.mitgliedschaft = get_valid_mitgliedschaft_based_on_mitgliedernummer(name)[0].name
	else:
		anfrage.mitgliedschaft = ''
	anfrage.save()
	
	return "ok"
	
@frappe.whitelist()
def create_new_mitglied(vorname='', nachname='', strasse='', hausnummer='', ort='', plz='', email='', telefon='', mobile=''):
	mitglied = frappe.get_doc({
		"doctype": "Customer",
		"customer_name": vorname + " " + nachname
	})
	mitglied.insert()
	
	address = frappe.get_doc({
		"doctype": "Address",
		"links": [
			{
				"link_doctype": "Customer",
				"link_name": mitglied.name
			}
		],
		"address_line1": strasse + " " + hausnummer,
		"city": ort,
		"pincode": plz,
		"email_id": email,
		"phone": telefon,
		"fax": mobile
	})
	address.insert()
	
	return mitglied.name
	
@frappe.whitelist()
def check_mitgliedschaft_ablaufdatum(mitgliedschaft):
	query = """SELECT * FROM `tabMitgliedschaft` WHERE `name` = '{mitgliedschaft}' AND `ende` >= CURDATE()""".format(mitgliedschaft=mitgliedschaft)
	if frappe.db.sql(query, as_dict=True):
		return True
	else:
		return False
		
@frappe.whitelist()
def get_timer_diff(start, ende):
	from frappe.utils.data import time_diff_in_seconds
	return time_diff_in_seconds(ende, start) / 60
	
@frappe.whitelist()
def get_dashboard_data(mitglied, anfrage):
	# Zeitbalken
	callcenter_limit = frappe.get_single("Einstellungen").limite_callcenter_anfrage
	callcenter_verwendet = frappe.get_doc("Anfrage", anfrage).timer
	limite_unterbruch = frappe.get_single("Einstellungen").limite_unterbruch
	
	# Mitgliedschaftsunterbruch Übersicht
	mitgliedschaften = frappe.db.sql("""SELECT `name`, `start`, `ende` FROM `tabMitgliedschaft` WHERE `rechnung` IN (
		SELECT `name` FROM `tabSales Invoice` WHERE `status` = 'Paid'
		) AND `mitglied` = '{mitglied}' ORDER BY `start` ASC""".format(mitglied=mitglied), as_dict=True)
		
	return {
			"callcenter_limit": callcenter_limit,
			"callcenter_verwendet": callcenter_verwendet,
			"mitgliedschaften": mitgliedschaften,
			"limite_unterbruch": limite_unterbruch
		}
			
@frappe.whitelist()
def check_rechnung(mitgliedschaft):
	mitgliedschaft = frappe.get_doc("Mitgliedschaft", mitgliedschaft)
	if not mitgliedschaft.rechnung:
		return "Keine Rechnung"
	else:
		rechnung = frappe.get_doc("Sales Invoice", mitgliedschaft.rechnung)
		return rechnung.status
		
@frappe.whitelist()
def creat_new_mandat(anfrage=None, mitglied=None):
	#check if Mandat linked to Anfrage already exist
	if anfrage:
		qty = frappe.db.sql("""SELECT COUNT(`name`) FROM `tabMandat` WHERE `anfragen` LIKE '%{anfrage}%'""".format(anfrage=anfrage), as_list=True)[0][0]
		if qty >= 1:
			return 'already exist'
			
	#creat new Mandat
	mandat = frappe.get_doc({
		"doctype": "Mandat"
	})
	
	mandat.insert()
	
	#If Anfrage available, set link
	if anfrage:
		mandat.update({
			'anfragen': anfrage
		})
		mandat.save()
		
	#If Mitglied available, set link
	if mitglied:
		mandat.update({
			'mitglied': mitglied
		})
		mandat.save()
	
	return mandat.name
