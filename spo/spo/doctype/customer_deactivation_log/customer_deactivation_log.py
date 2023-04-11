# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import now, getdate, date_diff

class CustomerDeactivationLog(Document):
	pass


def daily_check(today=False):
    month = frappe.get_single("Einstellungen").execution_month
    day = frappe.get_single("Einstellungen").execution_day
    if not today:
        today = getdate(now())
    else:
        today = getdate(today)
    
    # check for execution
    if int(str(month)) == int(today.strftime("%m")):
        if int(str(day)) == int(today.strftime("%d")):
            relevant_date = today.strftime("%Y-%m-%d")
            check_affected_sinvs(relevant_date)
            return
            
    # check for mail Notifications
    day_diff = date_diff('{year}-{month}-{day}'.format(year=today.strftime("%Y"), month=month, day=day), now())
    
    if day_diff == 7:
        send_pre_week_reminder()
        return
        
    if day_diff == 2:
        send_two_day_reminder()
        return
            
def check_affected_sinvs(relevant_date):
    sinvs = frappe.db.sql("""SELECT
                                `name`
                            FROM `tabSales Invoice`
                            WHERE
                                `docstatus` = 1
                                AND `status` = 'Overdue'
                                AND `payment_reminder_level` = 1
                                AND `exclude_from_payment_reminder_until` = '{relevant_date}'""".format(relevant_date=relevant_date), as_dict=True)
    if len(sinvs) > 0:
        accounts_frozen_upto = remove_accounts_frozen_upto()
        positiv_log = []
        negativ_log = []
        for sinv in sinvs:
            proceeded_sinv = proceed_sinv(sinv.name)
            if proceeded_sinv["status"]:
                positiv_log.append(proceeded_sinv)
            else:
                negativ_log.append(proceeded_sinv)
                
        create_log_record(positiv_log, negativ_log)
        if accounts_frozen_upto:
            reset_accounts_frozen_upto(accounts_frozen_upto)
            
def proceed_sinv(sinv):
    try:
        mitgliedschaft = frappe.db.sql("""SELECT
                                            `name`
                                        FROM `tabMitgliedschaft`
                                        WHERE
                                            `rechnung` = '{sinv}'""".format(sinv=sinv), as_dict=True)
        if len(mitgliedschaft) != 1:
            sinv_doc = frappe.get_doc("Sales Invoice", sinv)
            return {
                'status': False,
                'sales_invoice': sinv_doc.name,
                'customer': sinv_doc.customer,
                'mitgliedschaft': '',
                'error': 'Dieser Kunde besitzt mehrere Mitgliedschaften'
            }
            
        else:
            mitgliedschaft = frappe.get_doc("Mitgliedschaft", mitgliedschaft[0].name)
            mitgliedschaft.ende = mitgliedschaft.start
            mitgliedschaft.not_renew = 1
            mitgliedschaft.status = 'Inaktiviert'
            mitgliedschaft.status_bezugsdatum = getdate(now())
            mitgliedschaft.save()
            
            customer = frappe.get_doc("Customer", mitgliedschaft.mitglied)
            if customer.disabled == 1:
                customer.disabled = 0
                customer.save()
            
            sinv_doc = frappe.get_doc("Sales Invoice", sinv)
            cancel_linked_payment_reminder(sinv_doc.name)
            sinv_doc.cancel()
            
            customer = frappe.get_doc("Customer", mitgliedschaft.mitglied)
            customer.spo_aktuell = 'Kein'
            customer.disabled = 1
            customer.save()
            
            return {
                'status': True,
                'sales_invoice': sinv_doc.name,
                'customer': customer.name,
                'mitgliedschaft': mitgliedschaft.name
            }
            
    except Exception as err:
        # error handling
        sinv_doc = frappe.get_doc("Sales Invoice", sinv)
        return {
            'status': False,
            'sales_invoice': sinv_doc.name,
            'customer': sinv_doc.customer,
            'mitgliedschaft': '',
            'error': str(err)
        }
        
def create_log_record(positiv_log, negativ_log):
    log = frappe.get_doc({
        "doctype": "Customer Deactivation Log",
        "executed_on": getdate(now()),
        "deactivations": positiv_log,
        "errors": negativ_log
    })
    log.insert(ignore_links=True)
    
def cancel_linked_payment_reminder(sinv):
    pr = frappe.db.sql("""SELECT `parent` FROM `tabPayment Reminder Invoice` WHERE `sales_invoice` = '{sinv}' AND `docstatus` = 1""".format(sinv=sinv), as_dict=True)
    if len(pr) > 0:
        pr = frappe.get_doc("Payment Reminder", pr[0].parent)
        pr.cancel()

def send_pre_week_reminder():
    frappe.sendmail(recipients=get_recipients(), message="In einer Woche wird der automatisierte 'Kunden-Deaktivierungs-Prozess' gestartet. Bitte führen Sie noch einen Mahnungslauf durch.")
    return
    
def send_two_day_reminder():
    frappe.sendmail(recipients=get_recipients(), message="In zwei Tagen wird der automatisierte 'Kunden-Deaktivierungs-Prozess' gestartet. Bitte führen Sie noch einen Mahnungslauf durch.")
    return
    
def get_recipients():
    _recipients = frappe.get_single("Einstellungen").reminder_recipients
    recipients = []
    for _recipient in _recipients:
        recipients.append(_recipient.email)
    return recipients
    
def remove_accounts_frozen_upto():
    origin_value = frappe.db.get_single_value('Accounts Settings', 'acc_frozen_upto')
    if origin_value:
        frappe.db.sql("""UPDATE `tabSingles` SET `value` = '' WHERE `doctype` = 'Accounts Settings' AND `field` = 'acc_frozen_upto'""", as_list=True)
        frappe.db.commit()
        return origin_value
    else:
        return False
    
def reset_accounts_frozen_upto(origin_value):
    frappe.db.sql("""UPDATE `tabSingles` SET `value` = '{origin_value}' WHERE `doctype` = 'Accounts Settings' AND `field` = 'acc_frozen_upto'""".format(origin_value=origin_value), as_list=True)
    frappe.db.commit()
    return
