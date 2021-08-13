# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Meldestelle(Document):
	pass

def _create_reporting(**kwargs):
    '''
    call on [URL]/api/method/spo.api.create_reporting
    Mandatory Parameter:
        - fname: first name
        - lname: last name
        - phone: phone number
        - email: email address
        - availability: availability as text
        - report: reported message
    '''
    
    reported_data = kwargs
    try:
        new_reporting = frappe.get_doc({
            "doctype": "Meldestelle",
            "mandant": "KSA",
            "report_from": reported_data["fname"] + " " + reported_data["lname"],
            "phone": reported_data["phone"],
            "email": reported_data["email"],
            "availability": reported_data["availability"],
            "report": reported_data["report"]
        })
        new_reporting.insert(ignore_permissions=True)
        frappe.db.commit()
        
        status = '200 OK'
        answer = {
                "code": 200,
                "message": "OK"
            }

    except Exception as err:
        status = '400 Bad Request'
        answer = {
                "code": 400,
                "message": "{err}".format(err=err)
            }
        
    return [status, answer]
