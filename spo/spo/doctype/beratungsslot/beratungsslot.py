# -*- coding: utf-8 -*-
# Copyright (c) 2021-2023, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from spo.utils.payrexx import get_payment_status, create_payment
from frappe.utils import get_url
from datetime import date
from frappe.utils import cint

class Beratungsslot(Document):
    def fetch_payment_status(self):
        if self.payrexx_id:
            details = get_payment_status(payrexx_id=self.payrexx_id)
            self.payrexx_status = details['status']
            self.payrexx_url = details['link']
            if self.payrexx_status == "confirmed":
                self.status = "bezahlt"
                self.verify_payment()
            try:
                self.save(ignore_permissions=True)
            except Exception as err:
                # probably customer has been disabled (this prevents saving)
                frappe.log_error( "Unable to update {0} because {1}".format(self.name, err), "Payrexx fetch status error")
        return
    
    def create_payment(self):
        details = None
        sinv = frappe.get_all("Sales Invoice", filters={'beratungsslot': self.name},
            fields=['name', 'outstanding_amount', 'base_grand_total'])
        if len(sinv) > 0:
            details = create_payment(
                title="SPO Onlineberatung", 
                description="Onlinetermin bezahlen", 
                reference=self.name, 
                purpose="Onlineberatung", 
                amount=((sinv[0]['outstanding_amount'] or sinv[0]['base_grand_total']) * 100), 
                vat_rate=8.1, 
                sku=frappe.get_value("Einstellungen Onlinetermin", "Einstellungen Onlinetermin", "invoice_item"), 
                currency="CHF", 
                success_url="{0}?success={1}".format(get_url("onlinetermin"), self.name)
            )
            self.payrexx_id = details['id']
            self.payrexx_status = details['status']
            self.payrexx_url = details['link']
            if self.payrexx_status == "confirmed":
                self.status = "bezahlt"
                self.verify_payment()
            self.save(ignore_permissions=True)
        return details

    def verify_payment(self):
        # verify payment record
        sinv = frappe.get_all("Sales Invoice", 
            filters={'beratungsslot': self.name}, 
            fields=['name', 'outstanding_amount'])
        if len(sinv) > 0 and sinv[0]['outstanding_amount'] > 0:
            self.create_payment_record(sinv[0]['name'])
        return
    
    def create_payment_record(self, sinv):
        sinv_doc = frappe.get_doc("Sales Invoice", sinv)
        pe = frappe.get_doc({
            'doctype': 'Payment Entry',
            'payment_type': 'Receive',
            'party_type': 'Customer',
            'party': sinv_doc.customer,
            'posting_date': date.today(),
            'received_amount': sinv_doc.outstanding_amount,
            'paid_amount': sinv_doc.outstanding_amount,
            'paid_to': frappe.get_value("Einstellungen Onlinetermin", "Einstellungen Onlinetermin", "payrexx_account"),
            'reference_no': self.name,
            'reference_date': date.today(),
            'remarks': "Von Payrexx",
            'references': [{
                'reference_doctype': "Sales Invoice",
                'reference_name': sinv,
                'total_amount': sinv_doc.outstanding_amount,
                'outstanding_amount': sinv_doc.outstanding_amount,
                'allocated_amount': sinv_doc.outstanding_amount
            }]
        }) 
        pe.insert(ignore_permissions=True)
        pe.submit()
        return
        
@frappe.whitelist(allow_guest=True)
def get_slots(topic="Medizin"):
    available_slots = frappe.db.sql("""
        SELECT 
            `name` AS `id`, 
            "frei" AS `title`, 
            `topic` AS `description`,
            `start`, 
            `end`
        FROM `tabBeratungsslot`
        WHERE `start` >= DATE_ADD(DATE(NOW()), INTERVAL 2 DAY)
          AND `status` = "frei"
          AND `topic` = "{topic}";""".format(topic=topic), as_dict=True)
          
    return available_slots

@frappe.whitelist(allow_guest=True)
def reserve_slot(slot, member, first_name, last_name, address, 
    city, pincode, email, phone, used_slots=1, consultation_type="Online", 
    text="", geburtsdatum=None, salutation_title=None, ombudsstelle=None):
    # verify if this slot is still available
    available_slots = frappe.db.sql("""
        SELECT COUNT(`name`) AS `slots`
        FROM `tabBeratungsslot`
        WHERE `name` = "{slot}"
          AND `status` = "frei";""".format(slot=slot), as_dict=True)[0]['slots']
    if cint(available_slots) == 1:
        # slot available, reserve
        slot = frappe.get_doc("Beratungsslot", slot)
        slot.customer = member
        slot.first_name = first_name
        slot.last_name = last_name
        slot.address = address
        slot.city = city
        slot.pincode = pincode
        slot.email_id = email
        slot.phone = phone
        slot.consultation_type = consultation_type
        slot.text = text
        slot.geburtsdatum = geburtsdatum
        slot.salutation_title = salutation_title
        slot.ombudsstelle = ombudsstelle
        if cint(used_slots) == 0 or ombudsstelle:
            slot.status = "inklusive"
        else:
            slot.status = "reserviert"
        slot.save(ignore_permissions=True)
        return True
    else:
        # already taken
        return False
