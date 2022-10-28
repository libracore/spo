# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def demographie_bin_updater(record, event):
    quelle = record.doctype
    if not quelle:
        frappe.log_error("Keine Quellenangabe", 'Demographie Bin Updater')
        return
    if quelle != 'Customer':
        if quelle == 'Address' or quelle == 'Contact':
            for link in record.links:
                if link.link_doctype == 'Customer':
                    customer = frappe.get_doc("Customer", link.link_name)
                    customer.save()
        elif quelle == 'Mitgliedschaft':
            if record.mitglied:
                customer = frappe.get_doc("Customer", record.mitglied)
                customer.save()
            if record.rechnungsempfaenger:
                customer = frappe.get_doc("Customer", record.rechnungsempfaenger)
                customer.save()
        elif quelle == 'Payment Entry':
            if record.party_type == 'Customer' and record.party:
                customer = frappe.get_doc("Customer", record.party)
                customer.save()
    else:
        try:
            customer = record.name
            customer_doc = frappe.get_doc("Customer", customer)
            demographie_bin = check_existing_bin(customer)
            demographie_bin.aktuelle_mitgliedschaft = get_aktuelle_mitgliedschaft(customer)
            demographie_bin.eintrittsdatum = get_eintrittsdatum(customer)
            demographie_bin.zahlungen_total = get_zahlungen_total(customer)
            demographie_bin.mitgliedschafts_zahlungen = get_mitgliedschafts_zahlungen(customer)
            demographie_bin.spenden_zahlungen = get_spenden_zahlungen(customer)
            demographie_bin.spenden_auflistung = get_spenden_auflistung(customer)
            demographie_bin.letzte_bezahlte_periode = get_letzte_bezahlte_periode(customer)
            demographie_bin.letztes_zahlungsdatum = get_letztes_zahlungsdatum(customer)
            demographie_bin.anzahl_mitgliedschaften = get_anzahl_mitgliedschaften(customer)
            demographie_bin = get_mitgliedschafts_personen(demographie_bin)
            demographie_bin.mitgliedschaftstyp = get_mitgliedschaftstyp(customer)
            demographie_bin = get_adressdaten(demographie_bin)
            
            if len(demographie_bin.kontaktdaten) > 1 or len(demographie_bin.adressdaten) > 1:
                demographie_bin.multy_entry = 1
            else:
                demographie_bin.multy_entry = 0
            
            demographie_bin.save(ignore_permissions=True)
            
        except Exception as err:
            frappe.log_error("{0}".format(err), 'Demographie Bin Updater')
            return

def check_existing_bin(customer):
    if not frappe.db.exists('Demographie Bin', customer):
        new_bin = frappe.get_doc({
            "doctype": "Demographie Bin",
            "customer": customer,
        })
        new_bin.insert(ignore_permissions=True)
        return new_bin
    else:
        return frappe.get_doc("Demographie Bin", customer)

def get_aktuelle_mitgliedschaft(customer):
    mitgliedschaft = frappe.db.sql("""SELECT `name`
                                        FROM `tabMitgliedschaft`
                                        WHERE `mitglied` = '{customer}'
                                        ORDER BY `ende` DESC""".format(customer=customer), as_dict=True)
    if len(mitgliedschaft) > 0:
        return mitgliedschaft[0].name
    else:
        return None

def get_eintrittsdatum(customer):
    mitgliedschaft = frappe.db.sql("""SELECT `start`
                                        FROM `tabMitgliedschaft`
                                        WHERE `mitglied` = '{customer}'
                                        ORDER BY `start` ASC""".format(customer=customer), as_dict=True)
    if len(mitgliedschaft) > 0:
        return mitgliedschaft[0].start
    else:
        return None

def get_zahlungen_total(customer):
    amount = frappe.db.sql("""SELECT SUM(`paid_amount`) AS `amount`
                                FROM `tabPayment Entry`
                                WHERE `party` = '{customer}'
                                AND `payment_type` = 'Receive'
                                AND `docstatus` = 1""".format(customer=customer), as_dict=True)[0].amount
    if amount:
        return amount
    else:
        return 0

def get_mitgliedschafts_zahlungen(customer):
    mitgliedschafts_zahlungen = frappe.db.sql("""
                                        SELECT SUM(`grand_total`) AS `amount`
                                        FROM `tabSales Invoice`
                                        WHERE `name` IN (
                                            SELECT `rechnung`
                                            FROM `tabMitgliedschaft`
                                            WHERE `mitglied` = '{customer}'
                                        )
                                        AND `status` = 'Paid'""".format(customer=customer), as_dict=True)[0].amount
    if mitgliedschafts_zahlungen:
        return mitgliedschafts_zahlungen
    else:
        return 0

def get_spenden_zahlungen(customer):
    spenden_zahlungen = frappe.db.sql("""SELECT SUM(`amount`) AS `amount`
                                        FROM `tabPayment Entry Deduction`
                                        WHERE `parent` IN (
                                            SELECT `name`
                                            FROM `tabPayment Entry`
                                            WHERE `party` = '{customer}'
                                            AND `payment_type` = 'Receive'
                                            AND `docstatus` = 1
                                        )
                                        AND `parentfield` = 'deductions'
                                        AND `account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')""".format(customer=customer), as_dict=True)[0].amount
    if spenden_zahlungen:
        return spenden_zahlungen * -1
    else:
        return 0

def get_spenden_auflistung(customer):
    spenden_zahlungen_raw = frappe.db.sql("""SELECT SUM(`ped`.`amount`) AS `amount`,
                                        `pe`.`posting_date`
                                        FROM `tabPayment Entry Deduction` AS `ped`
                                        LEFT JOIN `tabPayment Entry` AS `pe` ON `ped`.`parent` = `pe`.`name`
                                        WHERE `ped`.`parent` IN (
                                            SELECT `name`
                                            FROM `tabPayment Entry`
                                            WHERE `party` = '{customer}'
                                            AND `payment_type` = 'Receive'
                                            AND `docstatus` = 1
                                        )
                                        AND `ped`.`parentfield` = 'deductions'
                                        AND `ped`.`account` IN ('3000 - Spenden - SPO', '3050 - Spenden - GöV')
                                        GROUP BY `pe`.`posting_date`
                                        ORDER BY `pe`.`posting_date` DESC""".format(customer=customer), as_dict=True)
    if len(spenden_zahlungen_raw) > 0:
        spenden_zahlungen = ''
        for sz in spenden_zahlungen_raw:
            spenden_zahlungen += "{0}: {1}\n".format(frappe.utils.get_datetime(sz.posting_date).strftime('%d.%m.%Y'), "{:,.2f}".format(sz.amount * -1).replace(",", "'"))
        return spenden_zahlungen
    else:
        return None

def get_letzte_bezahlte_periode(customer):
    rechnungen = frappe.db.sql("""SELECT `rechnung`, `start`, `ende`
                                        FROM `tabMitgliedschaft`
                                        WHERE `mitglied` = '{customer}'
                                        ORDER BY `ende` DESC""".format(customer=customer), as_dict=True)
    letzte_bezahlte_periode = None
    for rechnung in rechnungen:
        if frappe.db.get_value('Sales Invoice', rechnung.rechnung, 'status') == 'Paid':
            letzte_bezahlte_periode = "{0} bis {1}".format(frappe.utils.get_datetime(rechnung.start).strftime('%d.%m.%Y'), frappe.utils.get_datetime(rechnung.ende).strftime('%d.%m.%Y'))
            break
    return letzte_bezahlte_periode

def get_letztes_zahlungsdatum(customer):
    date = frappe.db.sql("""SELECT `posting_date`
                                FROM `tabPayment Entry`
                                WHERE `party` = '{customer}'
                                AND `payment_type` = 'Receive'
                                AND `docstatus` = 1
                                ORDER BY `posting_date` DESC""".format(customer=customer), as_dict=True)
    if len(date) > 0:
        return date[0].posting_date
    else:
        return None

def get_anzahl_mitgliedschaften(customer):
    mitgliedschaften = frappe.db.sql("""SELECT COUNT(`name`) AS `qty`
                                        FROM `tabMitgliedschaft`
                                        WHERE `mitglied` = '{customer}'""".format(customer=customer), as_dict=True)[0].qty
    return mitgliedschaften

def get_mitgliedschafts_personen(demographie_bin):
    customer = demographie_bin.customer
    kontakte = frappe.db.sql("""SELECT
                                    `first_name`,
                                    `last_name`,
                                    `salutation`,
                                    `geburtsdatum`,
                                    `mobile_no`,
                                    `email_id`,
                                    `is_primary_contact`
                                FROM `tabContact`
                                WHERE `name` IN (
                                    SELECT `parent`
                                    FROM `tabDynamic Link`
                                    WHERE `parenttype` = 'Contact'
                                    AND `link_name` = '{customer}'
                                )
                                ORDER BY `is_primary_contact` DESC""".format(customer=customer), as_dict=True)
    namen = ''
    kontaktliste = []
    demographie_bin.kontaktdaten = []
    for kontakt in kontakte:
        namen += "{0} {1}\n".format(kontakt.first_name, kontakt.last_name)
        row = demographie_bin.append('kontaktdaten', {})
        row.anrede = kontakt.salutation
        row.vorname = kontakt.first_name
        row.nachname = kontakt.last_name
        row.geburtsdatum = kontakt.geburtsdatum
        row.is_primary = kontakt.is_primary_contact
        row.mobile = kontakt.mobile_no
        row.mail = kontakt.email_id
    demographie_bin.mitgliedschafts_personen = namen
    return demographie_bin

def get_mitgliedschaftstyp(customer):
    mitgliedschaft = frappe.db.sql("""SELECT `mitgliedschafts_typ`
                                        FROM `tabMitgliedschaft`
                                        WHERE `mitglied` = '{customer}'
                                        ORDER BY `start` ASC""".format(customer=customer), as_dict=True)
    if len(mitgliedschaft) > 0:
        return mitgliedschaft[0].mitgliedschafts_typ
    else:
        return None

def get_adressdaten(demographie_bin):
    customer = demographie_bin.customer
    adressen = frappe.db.sql("""SELECT
                                    `address_line1`,
                                    `plz`,
                                    `city`,
                                    `kanton`
                                FROM `tabAddress`
                                WHERE `name` IN (
                                    SELECT `parent`
                                    FROM `tabDynamic Link`
                                    WHERE `parenttype` = 'Address'
                                    AND `link_name` = '{customer}'
                                )""".format(customer=customer), as_dict=True)
    adressliste = []
    demographie_bin.adressdaten = []
    for adresse in adressen:
        row = demographie_bin.append('adressdaten', {})
        row.strasse = adresse.address_line1
        row.plz = adresse.plz
        row.ort = adresse.city
        row.kanton = adresse.kanton
    return demographie_bin
