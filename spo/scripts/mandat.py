# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def creat_new_mandat(anfrage=None):
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
	
	return mandat.name