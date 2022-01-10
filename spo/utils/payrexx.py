# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import urllib.request
import requests
import hmac
import hashlib
import base64
import json
from datetime import date, timedelta

API_BASE = "https://api.payrexx.com/v1.0/"

def create_payment(title, description, reference, purpose, amount, 
    vat_rate, sku, currency, success_url):
    post_data = {
        "title": title,
        "description": description,
        "psp": 1,
        "referenceId": reference,
        "purpose": purpose,
        "amount": amount,
        "vatRate": vat_rate,
        "currency": currency,
        "sku": sku,
        "preAuthorization": 0,
        "reservation": 0,
        "successRedirectUrl": success_url
    }
    data = urllib.parse.urlencode(post_data).encode('utf-8')
    settings = frappe.get_doc("Einstellungen Onlinetermin", "Einstellungen Onlinetermin")
    if not settings.payrexx_api_key:
        frappe.throw( _("Bitte Payrexx Einstellungen in den Einstellungen Onlinetermin eintragen") )
    dig = hmac.new(settings.payrexx_api_key.encode('utf-8'), msg=data, digestmod=hashlib.sha256).digest()
    post_data['ApiSignature'] = base64.b64encode(dig).decode()
    data = urllib.parse.urlencode(post_data, quote_via=urllib.parse.quote).encode('utf-8')
    r = requests.post("{0}Invoice/?instance={1}".format(API_BASE, settings.payrexx_instance), data=data)
    response = json.loads(r.content.decode('utf-8'))
    invoice = response['data'][0]
    return invoice

def get_payment_status(payrexx_id):
    post_data = {}
    data = urllib.parse.urlencode(post_data).encode('utf-8')
    settings = frappe.get_doc("Einstellungen Onlinetermin", "Einstellungen Onlinetermin")
    if not settings.payrexx_api_key:
        frappe.throw( _("Bitte Payrexx Einstellungen in den Einstellungen Onlinetermin eintragen") )
    dig = hmac.new(settings.payrexx_api_key.encode('utf-8'), msg=data, digestmod=hashlib.sha256).digest()
    post_data['ApiSignature'] = base64.b64encode(dig).decode()
    data = urllib.parse.urlencode(post_data, quote_via=urllib.parse.quote).encode('utf-8')
    r = requests.get("{0}Invoice/{2}/?instance={1}".format(API_BASE, settings.payrexx_instance, payrexx_id), data=data)
    response = json.loads(r.content.decode('utf-8'))
    invoice = response['data'][0]
    return invoice


"""
This function will pull the payment status of all "waiting" payments (no older than 2 weeks)

Run on cron with bench execute spo.utils.payrexx.force_fetch_payment_status --kwargs "{'debug': False}"
"""
def force_fetch_payment_status(debug=False):
    waiting_payments = frappe.get_all("Beratungsslot", 
        filters=[
            ['payrexx_status', '=', 'waiting'], 
            ['start', '>=', (date.today() - timedelta(days=14))]
        ],
        fields=['name'])
    for payment in waiting_payments:
        slot = frappe.get_doc("Beratungsslot", payment['name'])
        if debug:
            print("Updating {0}".format(slot.name))
        slot.fetch_payment_status()
    return
