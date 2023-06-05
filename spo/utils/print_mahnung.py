# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, os
from frappe.model.document import Document
from frappe.utils.data import add_days, today, add_years, now
from PyPDF2 import PdfFileWriter
from frappe import _
from frappe.utils.pdf import get_file_data_from_writer

@frappe.whitelist()
def create_mahnungs_pdf(mahnung):
    if mahnung:
        print_bind(mahnung)
    else:
        return

def print_bind(mahnung):
    # Concatenating pdf files
    mahnung = frappe.get_doc("Payment Reminder", mahnung)
    output = PdfFileWriter()
    output = frappe.get_print("Payment Reminder", mahnung.name , 'SPO Zahlungserinnerung', as_pdf = True, output = output, ignore_zugferd=True)
    for sales_invoice in mahnung.sales_invoices:
        print_format = 'QR-Rechnung SPO' if sales_invoice.company == 'SPO Schweizerische Patientenorganisation' else 'Mitgliederrechnung'
        output = frappe.get_print("Sales Invoice", sales_invoice.sales_invoice, print_format, as_pdf = True, output = output, ignore_zugferd=True)
    
    file_name = "{mahnung}_{datetime}".format(mahnung=mahnung.name, datetime=now().replace(" ", "_"))
    file_name = file_name.split(".")[0]
    file_name = file_name.replace(":", "-")
    file_name = file_name + ".pdf"
    
    filedata = get_file_data_from_writer(output)
        
    _file = frappe.get_doc({
        "doctype": "File",
        "file_name": file_name,
        "folder": "Home/Attachments",
        "is_private": 1,
        "content": filedata,
        "attached_to_doctype": 'Payment Reminder',
        "attached_to_name": mahnung.name
    })
    _file.save(ignore_permissions=True)
