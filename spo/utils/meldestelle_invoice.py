# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def get_logs(meldestelle):
    meldestelle = frappe.get_doc("Meldestelle", meldestelle)
    logs = frappe.db.sql("""SELECT
                                `tabTimesheet Detail`.`hours`,
                                `tabTimesheet Detail`.`spo_dokument`,
                                `tabTimesheet Detail`.`spo_remark`,
                                `tabTimesheet Detail`.`from_time`,
                                `tabTimesheet Detail`.`owner`,
                                `employee` AS `employee_name`
                                FROM `tabTimesheet Detail`
                                INNER JOIN `tabEmployee` ON `tabTimesheet Detail`.`owner` = `tabEmployee`.`user_id`
                                WHERE
                                `tabTimesheet Detail`.`nicht_verrechnen` != 1
                                AND `tabTimesheet Detail`.`spo_referenz` = '{reference}'
                                ORDER BY `tabTimesheet Detail`.`from_time`, `tabTimesheet Detail`.`idx` ASC""".format(reference=meldestelle.name), as_dict=True)
    return {
            'logs': logs,
            'customer': meldestelle.customer
        }
