# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def get_mandat_logs(mandat):
    mandat = frappe.get_doc("Mandat", mandat)
    referenz_anfrage = mandat.anfragen
    if referenz_anfrage:
        referenz_anfrage = " OR `spo_referenz` = '{referenz_anfrage}'".format(referenz_anfrage=referenz_anfrage)
    else:
        referenz_anfrage = ''
    logs = frappe.db.sql("""SELECT
                                `tabTimesheet Detail`.`hours`,
                                `tabTimesheet Detail`.`spo_dokument`,
                                `tabTimesheet Detail`.`spo_remark`,
                                `tabTimesheet Detail`.`from_time`,
                                `tabTimesheet Detail`.`owner`,
                                `tabTimesheet Detail`.`klientenkontakt`,
                                `employee` AS `employee_name`
                                FROM `tabTimesheet Detail`
                                INNER JOIN `tabEmployee` ON `tabTimesheet Detail`.`owner` = `tabEmployee`.`user_id`
                                WHERE
                                `tabTimesheet Detail`.`nicht_verrechnen` != 1
                                AND `tabTimesheet Detail`.`spo_referenz` = '{reference}'
                                OR `tabTimesheet Detail`.`spo_referenz` IN (
                                    SELECT `name` FROM `tabAnforderung Patientendossier` WHERE `mandat` = '{reference}')
                                OR `tabTimesheet Detail`.`spo_referenz` IN (
                                    SELECT `name` FROM `tabMedizinischer Bericht` WHERE `mandat` = '{reference}')
                                OR `tabTimesheet Detail`.`spo_referenz` IN (
                                    SELECT `name` FROM `tabTriage` WHERE `mandat` = '{reference}')
                                OR `tabTimesheet Detail`.`spo_referenz` IN (
                                    SELECT `name` FROM `tabVollmacht` WHERE `mandat` = '{reference}')
                                OR `tabTimesheet Detail`.`spo_referenz` IN (
                                    SELECT `name` FROM `tabAbschlussbericht` WHERE `mandat` = '{reference}')
                                {referenz_anfrage}
                                ORDER BY `tabTimesheet Detail`.`from_time`, `tabTimesheet Detail`.`idx` ASC""".format(reference=mandat.name, referenz_anfrage=referenz_anfrage), as_dict=True)
    return {
            'logs': logs,
            'rsv': mandat.rsv,
            'rate': mandat.stundensatz,
            'ist_pauschal': True if mandat.pauschal_verrechnung else False,
            'pauschal_artikel': frappe.db.get_value('Einstellungen', 'Einstellungen', 'pauschal_artikel'),
            'pauschal_betrag': mandat.pauschal_betrag,
            'med_abschl_gespr': mandat.med_abschl_gespr,
            'med_abschl_gespr_betrag': frappe.db.get_value('Einstellungen', 'Einstellungen', 'med_abschl_gespr'),
            'med_abschl_gespr_datum': mandat.med_abschl_gespr_datum,
            'med_jur_abschl_gespr': mandat.med_jur_abschl_gespr,
            'med_jur_abschl_gespr_betrag': frappe.db.get_value('Einstellungen', 'Einstellungen', 'med_jur_abschl_gespr'),
            'med_jur_abschl_gespr_datum': mandat.med_jur_abschl_gespr_datum
        }
