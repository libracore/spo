# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Meldestelle(Document):
	pass

@frappe.whitelist(allow_guest=True)
def new_request(**kwargs):
    if kwargs:
        create_new_request(kwargs)
        
def create_new_request(kwargs):
    return
