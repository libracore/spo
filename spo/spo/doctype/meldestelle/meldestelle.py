# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests
import json

class Meldestelle(Document):
	pass


@frappe.whitelist(allow_guest=True)
def new_request():
    try:
        # get body
        data = frappe.local.form_dict 

        # verify reCAPTCHA   
        #secret = frappe.db.get_single_value('Einstellungen', 'recaptcha_secret')
        #payload = {'secret': secret, 'response': data['g-recaptcha-response']}
        #r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload)
        
        # reCAPTCHA valid
        if True: #r.json()['success']:
            nr = frappe.get_doc({
                "doctype": "Meldestelle",
                "mandant": data.mandant,
                "report_from": data.fname + " " + data.lname,
                "phone": data.phone,
                "email": data.email,
                "availability": data.availability,
                "report": data.report
            })
            nr.insert(ignore_permissions=True)
            return {
                'success': True
            }
        # reCAPTCHA invalid
        else:
            return {
                'success': False,
                'error': 'reCAPTCHA',
                'error-codes': r.json()['error-codes']
            }
    except Exception as err:
        frappe.log_error(err, "Meldestelle Error")
        return {
            'success': False,
            'error': "API Error"
        }
