# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import time
from spo.utils.payrexx import get_payment_status, create_payment

@frappe.whitelist(allow_guest=True) 
def get_active_partners():
	sql_query = """
		SELECT 
		IF (`tabOmbudsstellen Partner`.`active` = 1, `tabOmbudsstellen Partner`.`name`, null) AS active
		FROM `tabOmbudsstellen Partner`
		ORDER BY `tabOmbudsstellen Partner`.`active` DESC
	"""
	data = frappe.db.sql(sql_query, as_dict = True)
	return data

@frappe.whitelist(allow_guest=True)
def check_membership(member, lastname):
    # check if requests to API are accepted (fail block on 100 hits per day)
    failed = frappe.db.sql("""
    SELECT COUNT(`name`) AS `failed`
    FROM `tabOnlinetermin Access Log`
    WHERE `status` = "failed" 
      AND `creation` >= (DATE_SUB(NOW(), INTERVAL 1 DAY));""", as_dict=True)[0]['failed']
    if failed > 100:
        # gateway locked
        time.sleep(30)      # wait for 30 seconds
        return
    # validate customer
    customers = frappe.db.sql("""
        SELECT `tabCustomer`.`name`
        FROM `tabCustomer` 
        JOIN `tabDynamic Link` ON `tabDynamic Link`.`link_name` = `tabCustomer`.`name` 
            AND `tabDynamic Link`.`link_doctype` = "Customer" 
            AND `tabDynamic Link`.`parenttype` = "Contact"
        JOIN `tabContact` ON `tabContact`.`name` = `tabDynamic Link`.`parent`
        WHERE `tabCustomer`.`name` = "{member}"
          AND `tabContact`.`last_name` = "{lastname}";""".format(
            member=member, lastname=lastname), as_dict=True)
    if len(customers) == 0:
        # no hit, invalid entry, pause
        add_access_log(
            title="Mismatch: request to member {0} with lastname {1}".format(member, lastname), 
            status="failed"
        )
        time.sleep(30)      # wait for 30 seconds
        return
    else:
        # check if there is a membership
        memberships = frappe.db.sql("""
            SELECT `name`
            FROM `tabMitgliedschaft`
            WHERE `tabMitgliedschaft`.`customer` = "{member}"
              AND `tabMitgliedschaft`.`start` <= NOW()
              AND `tabMitgliedschaft`.`ende` >= NOW();""".format(member=member), as_dict=True)
        if len(memberships) == 0:
            # no membership, pause
            add_access_log(
                title="Mismatch: request to member {0} with lastname {1} (no membership)".format(member, lastname), 
                status="failed"
            )
            time.sleep(30)      # wait for 30 seconds
            return
        else:
            add_access_log(
                title="Request to member {0} with lastname {1}".format(member, lastname), 
                status="success"
            )
            # valid membership, check availability of free consulation
            used_slots = frappe.db.sql("""
                SELECT COUNT(`name`) AS `slots`
                FROM `tabBeratungsslot`
                WHERE `customer` = "{member}" 
                  AND DATE(`start`) >= (DATE_SUB(NOW(), INTERVAL 12 MONTH));""".format(member=member), as_dict=True)
            
            # return full contact details
            details = frappe.db.sql("""
                SELECT 
                    `tabCustomer`.`name` AS `member`,
                    `tabContact`.`first_name`,
                    `tabContact`.`last_name`,
                    `tabAddress`.`address_line1`,
                    `tabAddress`.`city`,
                    `tabAddress`.`pincode`,
                    `tabAddress`.`country`,
                    `tabContact`.`email_id`,
                    `tabContact`.`phone`
                FROM `tabCustomer` 
                JOIN `tabDynamic Link` AS `tDL1` ON `tDL1`.`link_name` = `tabCustomer`.`name` 
                    AND `tDL1`.`link_doctype` = "Customer" 
                    AND `tDL1`.`parenttype` = "Contact"
                JOIN `tabContact` ON `tabContact`.`name` = `tDL1`.`parent`
                JOIN `tabDynamic Link` AS `tDL2` ON `tDL2`.`link_name` = `tabCustomer`.`name` 
                    AND `tDL2`.`link_doctype` = "Customer" 
                    AND `tDL2`.`parenttype` = "Address"
                JOIN `tabAddress` ON `tabAddress`.`name` = `tDL2`.`parent`
                WHERE `tabCustomer`.`name` = "{member}"
                LIMIT 1;""".format(member=member), as_dict=True)
            if len(details) > 0:
                detail_record = details[0]
                detail_record['used_slots'] = used_slots[0]['slots']
                return detail_record
            else:
                # no valid record
                return

def add_access_log(title, status):
    log = frappe.get_doc({
        'doctype': 'Onlinetermin Access Log',
        'title': title,
        'status': status
    })
    log.insert(ignore_permissions=True)
    return

@frappe.whitelist(allow_guest=True)
def submit_request(slot, member, first_name, last_name, address, 
    city, pincode, email, phone, geburtsdatum, salutation_title):
    settings = frappe.get_doc("Einstellungen Onlinetermin", "Einstellungen Onlinetermin")
    if not member:
        # create a new customer profile
        customer = frappe.get_doc({
            'doctype': 'Customer',
            'customer_name': "{0} {1}".format(first_name, last_name),
            'customer_group': settings.customer_group,
            'territory': settings.territory,
            'customer_type': 'Individual'
        })
        customer = customer.insert(ignore_permissions=True)
        beratungsslot = frappe.get_doc("Beratungsslot", slot)
        beratungsslot.customer = customer.name
        beratungsslot.save(ignore_permissions=True)
        contact = frappe.get_doc({
            'doctype': 'Contact',
            'last_name': last_name,
            'first_name': first_name,
            'email_id': email,
            'phone': phone,
            'geburtsdatum': geburtsdatum,
            'salutation_title': salutation_title,
            'email_ids': [{
                    'email_id': email,
                    'is_primary': 1
            }],
            'phone_nos': [{
                    'phone': phone,
                    'is_primary_phone': 1
            }],
            'links': [{
                    'link_doctype': 'Customer',
                    'link_name': customer.name
            }]
        })
        contact = contact.insert(ignore_permissions=True)
        address = frappe.get_doc({
            'doctype': 'Address',
            'address_title': customer.name,
            'address_line1': address,
            'city': city,
            'plz': pincode,
            'pincode': pincode,
            'links': [{
                'link_doctype': 'Customer',
                'link_name': customer.name
            }]
        })
        address = address.insert(ignore_permissions=True)
        member = customer.name
    # create new sales invoice
    taxes = frappe.get_doc("Sales Taxes and Charges Template", settings.sales_taxes)
    invoice = frappe.get_doc({
        'doctype': 'Sales Invoice',
        'company': settings.company,
        'customer': member,
        'beratungsslot': slot,
        'items': [{
            'item_code': settings.invoice_item,
            'qty': 1,
            'rate': settings.rate,
            'description': slot
        }],
        'taxes_and_charges': settings.sales_taxes,
        'taxes': taxes.taxes
    })
    invoice = invoice.insert(ignore_permissions=True)
    invoice.submit()
    # return {'invoice': invoice.name, 'rate': (invoice.rounded_total or invoice.grand_total)}
    # create payrexx payment
    return create_payment(slot)
    

@frappe.whitelist(allow_guest=True)
def fetch_payment_status(booking):
    beratungsslot = frappe.get_doc("Beratungsslot", booking)
    beratungsslot.fetch_payment_status()
    return
    
@frappe.whitelist(allow_guest=True)
def create_payment(booking):
    beratungsslot = frappe.get_doc("Beratungsslot", booking)
    details = beratungsslot.create_payment()
    return details

@frappe.whitelist(allow_guest=True)
def get_topics():
    topics = frappe.get_all("Beratunsgthema", fields=['name'])
    topic_list = []
    for t in topics:
        topic_list.append(t['name'])
    return topic_list
