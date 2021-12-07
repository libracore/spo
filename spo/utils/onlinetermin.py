# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import time

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
                  AND `date` >= (DATE_SUB(NOW(), INTERVAL 12 MONTH));""".format(member=member), as_dict=True)
            
            # return full contact details
            details = frappe.db.sql("""
                SELECT 
                    `tabCustomer`.`name` AS `member`,
                    `tabContact`.`first_name`,
                    `tabContact`.`last_name`,
                    `tabAddress`.`address_line1`,
                    `tabAddress`.`city`,
                    `tabAddress`.`pincode`,
                    `tabAddress`.`country`
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