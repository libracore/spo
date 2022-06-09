# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from spo.utils.timesheet_handlings import handle_timesheet, get_total_ts_time, get_zeiten_uebersicht, create_default_ts_entry
from frappe.utils.data import today, add_days, nowdate, get_datetime_str, now_datetime

class Mandat(Document):
    def validate(self):
        if self.is_new() != True:
            if not self.default_ts:
                # create start ts buchung
                #default_time = get_default_time("Mandat")
                #handle_timesheet(frappe.session.user, self.doctype, self.name, default_time, '', nowdate())
                create_default_ts_entry(frappe.session.user, self.doctype, self.name, nowdate())
                self.default_ts = 1

    def onload(self):
        if self.is_new() != True:
            if float(self.timer or 0) != float(get_total_ts_time(self.doctype, self.name) or 0):
                self.timer = float(get_total_ts_time(self.doctype, self.name) or 0)
                self.nicht_verrechnen_total = float(get_total_ts_time(self.doctype, self.name, nicht_verrechnen_filter=True) or 0)
                self.timer_chf = float(get_total_ts_time(self.doctype, self.name) or 0) * self.stundensatz
                self.nicht_verrechnen_total_chf = float(get_total_ts_time(self.doctype, self.name, nicht_verrechnen_filter=True) or 0) * self.stundensatz
                self.total_verrechenbar = self.timer - self.nicht_verrechnen_total

def get_default_time(doctype):
    time = 0
    defaults = frappe.get_doc("Einstellungen").ts_defaults
    for default in defaults:
        if default.dokument == doctype:
            time = default.default_hours
            break
    return time

@frappe.whitelist()
def get_dashboard_data(mitglied='', anfrage='', mandat=''):
    # Zeitbalken
    callcenter_limit = frappe.get_single("Einstellungen").limite_mandat_time
    callcenter_verwendet = 0.000

    # ~ if not mitglied:
    # zeit aus anfrage & mandat
    try:
        callcenter_verwendet = float(frappe.db.sql("""SELECT
                                                        SUM(`hours`) FROM `tabTimesheet Detail`
                                                    WHERE (
                                                    (`spo_dokument` = 'Anfrage' AND `spo_referenz` = '{anfrage}')
                                                    OR (`spo_dokument` = 'Mandat' AND `spo_referenz` = '{mandat}')
                                                    OR (`spo_dokument` = 'Anforderung Patientendossier' AND `spo_referenz` IN (
                                                        SELECT `name` FROM `tabAnforderung Patientendossier` WHERE `mandat` = '{mandat}'))
                                                    OR (`spo_dokument` = 'Medizinischer Bericht' AND `spo_referenz` IN (
                                                        SELECT `name` FROM `tabMedizinischer Bericht` WHERE `mandat` = '{mandat}'))
                                                    OR (`spo_dokument` = 'Triage' AND `spo_referenz` IN (
                                                        SELECT `name` FROM `tabTriage` WHERE `mandat` = '{mandat}'))
                                                    OR (`spo_dokument` = 'Vollmacht' AND `spo_referenz` IN (
                                                        SELECT `name` FROM `tabVollmacht` WHERE `mandat` = '{mandat}'))
                                                    OR (`spo_dokument` = 'Abschlussbericht' AND `spo_referenz` IN (
                                                        SELECT `name` FROM `tabAbschlussbericht` WHERE `mandat` = '{mandat}'))
                                                    )
                                                    AND `parent` IN (
                                                        SELECT `name` FROM `tabTimesheet` WHERE `docstatus` != 2)
                                                    AND `nicht_verrechnen` != 1""".format(anfrage=anfrage, mandat=mandat), as_list=True)[0][0])
    except:
        callcenter_verwendet = 0
    # ~ callcenter_verwendet = callcenter_verwendet * 60
    
    try:
        nicht_verrechnen = float(frappe.db.sql("""SELECT
                                                        SUM(`hours`) FROM `tabTimesheet Detail`
                                                    WHERE (
                                                    (`spo_dokument` = 'Anfrage' AND `spo_referenz` = '{anfrage}')
                                                    OR (`spo_dokument` = 'Mandat' AND `spo_referenz` = '{mandat}')
                                                    OR (`spo_dokument` = 'Anforderung Patientendossier' AND `spo_referenz` IN (
                                                        SELECT `name` FROM `tabAnforderung Patientendossier` WHERE `mandat` = '{mandat}'))
                                                    OR (`spo_dokument` = 'Medizinischer Bericht' AND `spo_referenz` IN (
                                                        SELECT `name` FROM `tabMedizinischer Bericht` WHERE `mandat` = '{mandat}'))
                                                    OR (`spo_dokument` = 'Triage' AND `spo_referenz` IN (
                                                        SELECT `name` FROM `tabTriage` WHERE `mandat` = '{mandat}'))
                                                    OR (`spo_dokument` = 'Vollmacht' AND `spo_referenz` IN (
                                                        SELECT `name` FROM `tabVollmacht` WHERE `mandat` = '{mandat}'))
                                                    OR (`spo_dokument` = 'Abschlussbericht' AND `spo_referenz` IN (
                                                        SELECT `name` FROM `tabAbschlussbericht` WHERE `mandat` = '{mandat}'))
                                                    )
                                                    AND `parent` IN (
                                                        SELECT `name` FROM `tabTimesheet` WHERE `docstatus` != 2)
                                                    AND `nicht_verrechnen` = 1""".format(anfrage=anfrage, mandat=mandat), as_list=True)[0][0])
    except:
        nicht_verrechnen = 0
    # ~ nicht_verrechnen = nicht_verrechnen * 60
    
        
    return {
            "callcenter_limit": callcenter_limit,
            "callcenter_verwendet": callcenter_verwendet,
            "nicht_verrechnen": nicht_verrechnen
        }

@frappe.whitelist()
def create_zeiten_uebersicht(dt, name):
    alle_zeiten = get_zeiten_uebersicht(dt, name)
    if alle_zeiten:
        html = '<div style="width: 100%;"><table style="width: 100%;" class="table-striped"><tr><th>Datum</th><th>Dokument</th><th>Arbeit</th><th>Stunden</th><th>Timesheet</th><th>Bearbeiten</th></tr>'
        for zeit in alle_zeiten:
            if not zeit.spo_remark:
                zeit.spo_remark = ''
            html += '<tr><td>' + get_datetime_str(zeit.from_time).split(" ")[0] + '</td><td>' + zeit.spo_dokument + ' (' + zeit.spo_referenz + ')</td><td>' + str(zeit.spo_remark) + '</td><td>' + str(zeit.hours) + '</td><td>' + zeit.parent + '</td><td><a data-referenz="' + zeit.parent + '" data-funktion="open_ts"><i class="fa fa-edit"></i></a></td></tr>'
        html += '</table></div>'
        return html
    else:
        return False

@frappe.whitelist()
def share_mandat_and_related_docs(mandat, user_to_add):
    related_docs = ['Vollmacht', 'Anforderung Patientendossier', 'Medizinischer Bericht', 'Triage', 'Abschlussbericht', 'Freies Schreiben', 'SPO Anhang']
    for related_doc in related_docs:
        doc_type = related_doc
        doc_names = frappe.db.sql("""SELECT `name` FROM `tab{doc_type}` WHERE `mandat` = '{mandat}'""".format(doc_type=doc_type, mandat=mandat), as_dict=True)
        for doc_name in doc_names:
            doc_name = doc_name.name
            # check if already exist and update if neccesary
            existing = frappe.db.sql("""SELECT `name` FROM `tabDocShare` WHERE `user` = '{user_to_add}' AND `share_doctype` = '{doc_type}' AND `share_name` = '{doc_name}'""".format(user_to_add=user_to_add, doc_type=doc_type, doc_name=doc_name), as_dict=True)
            if len(existing) > 0:
                for shared_doc in existing:
                    frappe.db.sql("""UPDATE `tabDocShare` SET `read` = 1, `share` = 1, `write` = 1, `modified` = '{datetime}' WHERE `name` = '{name}'""".format(name=shared_doc.name, datetime=now_datetime()), as_list=True)
            else:
                # if not exist, create new
                hash = frappe.generate_hash('DocShare', 10)
                frappe.db.sql("""INSERT INTO `tabDocShare`
                                    (`name`, `creation`, `modified`, `modified_by`, `owner`, `docstatus`, `idx`, `everyone`, `share_name`, `read`, `share`, `write`, `notify_by_email`, `user`, `share_doctype`)
                                    VALUES ('{hash}', '{datetime}', '{datetime}', '{user}', '{user}', 0, 0, 0, '{doc_name}', 1, 1, 1, 1, '{user_to_add}', '{doc_type}')""".format(hash=hash, datetime=now_datetime(), user=frappe.session.user, doc_name=doc_name, user_to_add=user_to_add, doc_type=doc_type), as_list=True)
            
            
    doc_type = 'Mandat'
    doc_name = mandat
    # check if already exist and update if neccesary
    existing = frappe.db.sql("""SELECT `name` FROM `tabDocShare` WHERE `user` = '{user_to_add}' AND `share_doctype` = '{doc_type}' AND `share_name` = '{doc_name}'""".format(user_to_add=user_to_add, doc_type=doc_type, doc_name=doc_name), as_dict=True)
    if len(existing) > 0:
        for shared_doc in existing:
            frappe.db.sql("""UPDATE `tabDocShare` SET `read` = 1, `share` = 1, `write` = 1, `modified` = '{datetime}' WHERE `name` = '{name}'""".format(name=shared_doc.name, datetime=now_datetime()), as_list=True)
    else:
        # if not exist, create new
        hash = frappe.generate_hash('DocShare', 10)
        frappe.db.sql("""INSERT INTO `tabDocShare`
                            (`name`, `creation`, `modified`, `modified_by`, `owner`, `docstatus`, `idx`, `everyone`, `share_name`, `read`, `share`, `write`, `notify_by_email`, `user`, `share_doctype`)
                            VALUES ('{hash}', '{datetime}', '{datetime}', '{user}', '{user}', 0, 0, 0, '{doc_name}', 1, 1, 1, 1, '{user_to_add}', '{doc_type}')""".format(hash=hash, datetime=now_datetime(), user=frappe.session.user, doc_name=doc_name, user_to_add=user_to_add, doc_type=doc_type), as_list=True)
                            
    frappe.db.commit()
    return 'ok'

@frappe.whitelist()
def remove_share_of_mandat_and_related_docs(mandat, user_to_remove):
    related_docs = ['Vollmacht', 'Anforderung Patientendossier', 'Medizinischer Bericht', 'Triage', 'Abschlussbericht', 'Freies Schreiben', 'SPO Anhang']
    for related_doc in related_docs:
        doc_type = related_doc
        doc_names = frappe.db.sql("""SELECT `name` FROM `tab{doc_type}` WHERE `mandat` = '{mandat}'""".format(doc_type=doc_type, mandat=mandat), as_dict=True)
        for doc_name in doc_names:
            doc_name = doc_name.name
            # check if already exist and update
            existing = frappe.db.sql("""SELECT `name` FROM `tabDocShare` WHERE `user` = '{user_to_remove}' AND `share_doctype` = '{doc_type}' AND `share_name` = '{doc_name}'""".format(user_to_remove=user_to_remove, doc_type=doc_type, doc_name=doc_name), as_dict=True)
            if len(existing) > 0:
                for shared_doc in existing:
                    frappe.db.sql("""UPDATE `tabDocShare` SET `read` = 0, `share` = 0, `write` = 0, `modified` = '{datetime}' WHERE `name` = '{name}'""".format(name=shared_doc.name, datetime=now_datetime()), as_list=True)
            
    doc_type = 'Mandat'
    doc_name = mandat
    # check if already exist and update
    existing = frappe.db.sql("""SELECT `name` FROM `tabDocShare` WHERE `user` = '{user_to_remove}' AND `share_doctype` = '{doc_type}' AND `share_name` = '{doc_name}'""".format(user_to_remove=user_to_remove, doc_type=doc_type, doc_name=doc_name), as_dict=True)
    if len(existing) > 0:
        for shared_doc in existing:
            frappe.db.sql("""UPDATE `tabDocShare` SET `read` = 0, `share` = 0, `write` = 0, `modified` = '{datetime}' WHERE `name` = '{name}'""".format(name=shared_doc.name, datetime=now_datetime()), as_list=True)
                            
    frappe.db.commit()
    return 'ok'

@frappe.whitelist()
def get_facharzt_table(customer=None, type=None):
    results = []
    filter = ''
    if customer or type:
        filter = ' WHERE '
    if customer:
        filter += " `supplier_name` LIKE '%{customer}%'".format(customer=customer)
    if type:
        if customer:
            filter += " AND `supplier_group` = '{type}'".format(type=type)
        else:
            filter += " `supplier_group` = '{type}'".format(type=type)
            
    #search facharzt
    facharzt_results = frappe.db.sql("""SELECT
                                            `name` AS `reference`,
                                            `name` AS `Link Name`,
                                            `supplier_name` AS `Facharzt`,
                                            `supplier_group` AS `Type`
                                            FROM `tabSupplier`{filter}""".format(filter=filter), as_dict=True)
                                            
    for facharzt_result in facharzt_results:
        results.append(facharzt_result)

    if results:
        return results
    else:
        return False

@frappe.whitelist()
def create_new_facharzt_bericht(mandat, facharzt):
    facharzt_bericht = frappe.get_doc({
        "doctype": "Facharzt Bericht",
        "mandat": mandat,
        "facharzt": facharzt
    })
    facharzt_bericht.insert(ignore_permissions=True)
    return facharzt_bericht.name

@frappe.whitelist()
def erstelle_mandats_revision(mandat):
    mandat = frappe.get_doc("Mandat", mandat)
    
    new_mandat = frappe.copy_doc(mandat)
    new_mandat.docstatus = 0
    if not mandat.ursprungs_mandat:
        new_mandat.ursprungs_mandat = mandat.name
        new_name = mandat.name + "-1"
    else:
        if len(mandat.ursprungs_mandat.split("-")) > 3:
            revision = str(int(mandat.ursprungs_mandat.split("-")[3]) + 2)
        else:
            revision = '2'
        new_mandat.ursprungs_mandat = mandat.name
        new_name = mandat.name.split("-")[0] + "-" + mandat.name.split("-")[1] + "-" + mandat.name.split("-")[2] + "-" + revision
    new_mandat.anfragen = ''
    new_mandat.insert()
    
    frappe.rename_doc('Mandat', new_mandat.name, new_name)
    copy_attachments_from_mandat(mandat.name, new_name)
    
    return new_name

def copy_attachments_from_mandat(mandat, new_mandat):
    from frappe.desk.form.load import get_attachments

    # loop through attachments
    for attach_item in get_attachments('Mandat', mandat):
        # save attachments to new doc
        _file = frappe.get_doc({
            "doctype": "File",
            "file_url": attach_item.file_url,
            "file_name": attach_item.file_name,
            "attached_to_name": new_mandat,
            "attached_to_doctype": 'Mandat',
            "folder": "Home/Attachments"})
        _file.save()
