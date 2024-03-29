# -*- coding: utf-8 -*-
# Copyright (c) 2019, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import today, add_days, nowdate, get_datetime_str
from spo.utils.timesheet_handlings import handle_timesheet, get_total_ts_time, get_zeiten_uebersicht, create_default_ts_entry
from frappe.utils import validate_email_address

class Anfrage(Document):
    def validate(self):
        if self.is_new() != True:
            if not self.default_ts:
                # create start ts buchung
                #handle_timesheet(frappe.session.user, self.doctype, self.name, 0, '', self.datum)
                onlineberatung = False
                if self.anfrage_typ == 'Online-Beratung':
                    onlineberatung = True
                create_default_ts_entry(frappe.session.user, self.doctype, self.name, self.datum, onlineberatung=onlineberatung)
                self.default_ts = 1

        if self.patient != self.customer:
            self.customer = self.patient
        
        if self.eingeschraenkter_zugriff:
            self.spo_vip_status = 'VIP'
        else:
            self.spo_vip_status = 'Normal'
        
        if self.kontakt_via == 'Upload Tool':
            if not self.rsv_adresse:
                if self.rsv:
                    rsv_adressen = frappe.db.sql("""
                                                    SELECT
                                                        `parent`
                                                    FROM `tabDynamic Link`
                                                    WHERE `parenttype` = 'Address'
                                                    AND `link_name` = '{0}'""".format(self.rsv), as_dict=True)
                    
                    if len(rsv_adressen) > 0:
                        self.rsv_adresse = rsv_adressen[0].parent

    def onload(self):
        if self.is_new() != True:
            if float(self.timer or 0) != float(get_total_ts_time(self.doctype, self.name) or 0):
                self.timer = float(get_total_ts_time(self.doctype, self.name) or 0)


def kpi_refresh():
    records = frappe.db.sql("""SELECT `name` FROM `tabAnfrage` WHERE `docstatus` NOT IN (1, 2)""", as_dict=True)
    for record in records:
        self = frappe.get_doc('Anfrage', record.name)
        if self.is_new() != True:
            if float(self.timer or 0) != float(get_total_ts_time(self.doctype, self.name) or 0):
                timer_value = float(get_total_ts_time(self.doctype, self.name) or 0)
                frappe.db.set_value('Anfrage', self.name, 'timer', timer_value)

@frappe.whitelist()
def get_valid_mitgliedschaft_based_on_mitgliedernummer(mitgliedernummer):
    query = """SELECT * FROM `tabMitgliedschaft` WHERE `mitglied` = '{mitgliedernummer}' AND `ende` >= CURDATE()""".format(mitgliedernummer=mitgliedernummer)
    return frappe.db.sql(query, as_dict=True)

@frappe.whitelist()
def create_new_mitglied(vorname='', nachname='', strasse='', ort='', plz='', email='', telefon='', mobile='', geburtsdatum='', kanton='', adress_zusatz=''):
    mitglied = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": vorname + " " + nachname
    })
    mitglied.insert()

    if kanton == '' or kanton == 'Keine Angabe':
        kanton = 'ZH'

    address = frappe.get_doc({
        "doctype": "Address",
        "links": [
            {
                "link_doctype": "Customer",
                "link_name": mitglied.name
            }
        ],
        "address_line1": strasse,
        "address_line2": adress_zusatz,
        "city": ort,
        "plz": plz,
        "pincode": plz,
        "kanton": kanton
    })
    address.insert()

    if not validate_email_address(email):
        contact = frappe.get_doc({
            "doctype": "Contact",
            "links": [
                {
                    "link_doctype": "Customer",
                    "link_name": mitglied.name
                }
            ],
            "geburtsdatum": geburtsdatum,
            "first_name": vorname,
            "last_name": nachname
        })
        contact.insert()
    else:
        contact = frappe.get_doc({
            "doctype": "Contact",
            "links": [
                {
                    "link_doctype": "Customer",
                    "link_name": mitglied.name
                }
            ],
            "geburtsdatum": geburtsdatum,
            "first_name": vorname,
            "last_name": nachname,
            "email_ids": [
                {
                    "email_id": email,
                    "is_primary": 1
                }
            ]
        })
        contact.insert()

    if telefon and mobile:
        contact.update({
            "phone_nos": [
                {
                    "phone": telefon,
                    "is_primary_phone": 1
                },
                {
                    "phone": mobile,
                    "is_primary_mobile_no": 1
                }
            ]
        })
        contact.save()
    elif mobile:
        contact.update({
            "phone_nos": [
                {
                    "phone": mobile,
                    "is_primary_mobile_no": 1
                }
            ]
        })
        contact.save()
    elif telefon:
        contact.update({
            "phone_nos": [
                {
                    "phone": telefon,
                    "is_primary_phone": 1
                }
            ]
        })
        contact.save()
    return {
            'patient': mitglied.name,
            'patienten_kontakt': contact.name,
            'patienten_adresse': address.name
        }

@frappe.whitelist()
def check_mitgliedschaft_ablaufdatum(mitgliedschaft):
    query = """SELECT * FROM `tabMitgliedschaft` WHERE `name` = '{mitgliedschaft}' AND `ende` >= CURDATE()""".format(mitgliedschaft=mitgliedschaft)
    if frappe.db.sql(query, as_dict=True):
        return True
    else:
        return False

@frappe.whitelist()
def get_dashboard_data(mitglied='', anfrage='', mitgliedschaft=''):
    # Zeitbalken
    callcenter_limit = frappe.get_single("Einstellungen").limite_callcenter_anfrage
    callcenter_verwendet = 0.000
    if not mitglied:
        try:
            callcenter_verwendet = float(frappe.db.sql("""SELECT SUM(`hours`) FROM `tabTimesheet Detail` WHERE `spo_dokument` = 'Anfrage' AND `spo_referenz` = '{anfrage}' AND `parent` IN (
                                                        SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 OR `docstatus` = 1)""".format(anfrage=anfrage), as_list=True)[0][0])
        except:
            callcenter_verwendet = 0
        callcenter_verwendet = callcenter_verwendet * 60
    else:
        if not mitgliedschaft:
            try:
                callcenter_verwendet = float(frappe.db.sql("""SELECT SUM(`hours`) FROM `tabTimesheet Detail` WHERE `spo_dokument` = 'Anfrage' AND `spo_referenz` IN (
                                                            SELECT `name` FROM `tabAnfrage` WHERE `patient` = '{mitglied}')
                                                            AND `parent` IN (
                                                                SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 OR `docstatus` = 1)""".format(anfrage=anfrage, mitglied=mitglied), as_list=True)[0][0])
            except:
                callcenter_verwendet = 0
            callcenter_verwendet = callcenter_verwendet * 60
        else:
            try:
                callcenter_verwendet = float(frappe.db.sql("""SELECT SUM(`hours`) FROM `tabTimesheet Detail` WHERE `spo_dokument` = 'Anfrage' AND `spo_referenz` IN (
                                                            SELECT `name` FROM `tabAnfrage` WHERE `patient` = '{mitglied}' AND `mitgliedschaft` = '{mitgliedschaft}')
                                                            AND `parent` IN (
                                                                SELECT `name` FROM `tabTimesheet` WHERE `docstatus` = 0 OR `docstatus` = 1)""".format(anfrage=anfrage, mitglied=mitglied, mitgliedschaft=mitgliedschaft), as_list=True)[0][0])
            except:
                callcenter_verwendet = 0
            callcenter_verwendet = callcenter_verwendet * 60

    limite_unterbruch = frappe.get_single("Einstellungen").limite_unterbruch

    # Mitgliedschaftsunterbruch Übersicht
    if mitglied:
        mitgliedschaften = frappe.db.sql("""SELECT `name`, `start`, `ende` FROM `tabMitgliedschaft` WHERE `rechnung` IN (
            SELECT `name` FROM `tabSales Invoice` WHERE `status` = 'Paid'
            ) AND `mitglied` = '{mitglied}' ORDER BY `start` ASC""".format(mitglied=mitglied), as_dict=True)
    else:
        mitgliedschaften = 'keine'

    return {
            "callcenter_limit": callcenter_limit,
            "callcenter_verwendet": round(callcenter_verwendet),
            "mitgliedschaften": mitgliedschaften,
            "limite_unterbruch": limite_unterbruch
        }

@frappe.whitelist()
def check_rechnung(mitgliedschaft):
    mitgliedschaft = frappe.get_doc("Mitgliedschaft", mitgliedschaft)
    if not mitgliedschaft.rechnung:
        return "Keine Rechnung"
    else:
        rechnung = frappe.get_doc("Sales Invoice", mitgliedschaft.rechnung)
        return rechnung.status

@frappe.whitelist()
def creat_new_mandat(anfrage=None, mitglied=None, kontakt=None, adresse=None, rsv=None, rsv_kontakt=None, rsv_adresse=None, rsv_ref=None, ang=None, ang_kontakt=None, ang_adresse=None, ges_ver_1=None, ges_ver_1_adresse=None, ges_ver_1_kontakt=None, ges_ver_2=None, ges_ver_2_adresse=None, ges_ver_2_kontakt=None):
    #check if Mandat linked to Anfrage already exist
    if anfrage:
        qty = frappe.db.sql("""SELECT COUNT(`name`) FROM `tabMandat` WHERE `anfragen` LIKE '%{anfrage}%'""".format(anfrage=anfrage), as_list=True)[0][0]
        if qty >= 1:
            return 'already exist'

    #creat new Mandat
    mandat = frappe.get_doc({
        "doctype": "Mandat"
    })

    mandat.insert(ignore_permissions=True)

    #If Anfrage available, set link
    if anfrage:
        mandat.update({
            'anfragen': anfrage
        })
        mandat.save()

    #If Mitglied available, set link
    if mitglied:
        mandat.update({
            'mitglied': mitglied
        })
        mandat.save()

    #If adresse available, set link
    if adresse:
        mandat.update({
            'adresse': adresse
        })
        mandat.save()

    #If kontakt available, set link
    if kontakt:
        mandat.update({
            'kontakt': kontakt
        })
        mandat.save()

    #If rsv available, set link
    if rsv:
        mandat.update({
            'rsv': rsv
        })
        mandat.save()

    #If rsv_kontakt available, set link
    if rsv_kontakt:
        mandat.update({
            'rsv_kontakt': rsv_kontakt
        })
        mandat.save()

    #If rsv_adresse available, set link
    if rsv_adresse:
        mandat.update({
            'rsv_adresse': rsv_adresse
        })
        mandat.save()

    #If rsv_ref available, set link
    if rsv_ref:
        mandat.update({
            'rechtsschutz_ref': rsv_ref
        })
        mandat.save()

    #If ang available, set link
    if ang:
        mandat.update({
            'ang': ang
        })
        mandat.save()

    #If ang_kontakt available, set link
    if ang_kontakt:
        mandat.update({
            'ang_kontakt': ang_kontakt
        })
        mandat.save()

    #If ang_adresse available, set link
    if ang_adresse:
        mandat.update({
            'ang_adresse': ang_adresse
        })
        mandat.save()

    #If ges_ver_1 available, set link
    if ges_ver_1:
        mandat.update({
            'ges_ver_1': ges_ver_1
        })
        mandat.save()

    #If ges_ver_1_adresse available, set link
    if ges_ver_1_adresse:
        mandat.update({
            'ges_ver_1_adresse': ges_ver_1_adresse
        })
        mandat.save()

    #If ges_ver_1_kontakt available, set link
    if ges_ver_1_kontakt:
        mandat.update({
            'ges_ver_1_kontakt': ges_ver_1_kontakt
        })
        mandat.save()

    #If ges_ver_2 available, set link
    if ges_ver_2:
        mandat.update({
            'ges_ver_2': ges_ver_2
        })
        mandat.save()

    #If ges_ver_2_adresse available, set link
    if ges_ver_2_adresse:
        mandat.update({
            'ges_ver_2_adresse': ges_ver_2_adresse
        })
        mandat.save()

    #If ges_ver_2_kontakt available, set link
    if ges_ver_2_kontakt:
        mandat.update({
            'ges_ver_2_kontakt': ges_ver_2_kontakt
        })
        mandat.save()
    
    # relink files from anfrage to mandat
    anfrage_files = frappe.db.sql("""SELECT `name` FROM `tabFile` WHERE `attached_to_name` = '{0}'""".format(anfrage), as_dict=True)
    if len(anfrage_files) > 0:
        for anfrage_file in anfrage_files:
            frappe.db.set_value("File", anfrage_file.name, "attached_to_doctype", "Mandat")
            frappe.db.set_value("File", anfrage_file.name, "attached_to_name", mandat.name)


    return mandat.name

def autom_submit():
    sql_query = """SELECT
                        `name`
                    FROM `tabAnfrage`
                    WHERE (
                        `datum` <= '{last_14_days}' AND `docstatus` = 0 AND `anfrage_typ` = 'Mandats Anfrage'
                    ) OR (
                        `datum` <= '{last_week}' AND `docstatus` = 0 AND `anfrage_typ` != 'Mandats Anfrage'
                    )""".format(last_week=add_days(nowdate(), -7), last_14_days=add_days(nowdate(), -14))
    anfragen_to_submit = frappe.db.sql(sql_query, as_dict=True)
    for _anfrage in anfragen_to_submit:
        try:
            anfrage = frappe.get_doc("Anfrage", _anfrage.name)
            anfrage.timer = float(get_total_ts_time("Anfrage", anfrage.name) or 0)
            anfrage.save()
            anfrage.submit()
        except:
            try:
                anfrage = frappe.get_doc("Anfrage", _anfrage.name)
                customer = frappe.get_doc("Customer", anfrage.customer)
                customer.disabled = 0
                customer.save()
                anfrage.timer = float(get_total_ts_time("Anfrage", anfrage.name) or 0)
                anfrage.save()
                anfrage.submit()
                customer.disabled = 1
                customer.save()
            except:
                pass

@frappe.whitelist()
def check_anfrage_daten_vs_stamm_daten(vorname, nachname, geburtsdatum, kanton, strasse, ort, plz, telefon, mobile, email, patient, kontakt, adresse, adress_zusatz):
    customer = frappe.get_doc("Customer", patient)
    address = frappe.get_doc("Address", adresse)
    contact = frappe.get_doc("Contact", kontakt)
    abweichungen = ''

    #vor- Nachnamen
    _name_diff = True
    if (vorname + " " + nachname) == customer.customer_name:
        _name_diff = False
    if (nachname + " " + vorname) == customer.customer_name:
        _name_diff = False
    if _name_diff:
        abweichungen = '<h3>Name</h3><b>Alt/Neu:</b><br>' + str(customer.customer_name) + ' / ' + (str(vorname) or 'Kein Vorname') + " " + (str(nachname) or 'Kein Nachnamen') + '<br>'

    #adresse
    _address_diff = False
    if address.address_line1 != strasse:
        _address_diff = True
    if address.address_line2 != adress_zusatz:
        _address_diff = True
    if (str(address.plz) + " " + address.city) != (str(plz) + " " + ort):
        _address_diff = True
    if _address_diff:
        abweichungen += '<h3>Adresse</h3><b>Alt/Neu:</b><br>' + str(address.address_line1) + ' / '  + (str(strasse) or 'Keine Strasse') + '<br>' + str(address.address_line2) + ' / '  + (str(adress_zusatz) or 'Kein Adress-Zusatz') + '<br>' + str(address.pincode) + " " + str(address.city) + ' / '  + (str(plz) or 'Keine Postleitzahl') + " " + (str(ort) or 'Kein Ort') + '<br>'

    #contact
    _contact_diff = False
    if email != contact.email_id:
        _contact_diff = True
    if str(geburtsdatum) != str(contact.geburtsdatum):
        _contact_diff = True
    if telefon != contact.phone:
        _contact_diff = True
    if mobile != contact.mobile_no:
        _contact_diff = True
    if _contact_diff:
        abweichungen += '<h3>Kontakt</h3><b>Alt:/Neu</b><br>E-Mail: ' + str(contact.email_id) + ' / ' + (str(email) or 'Keine E-Mail') + '<br>Telefon: ' + str(contact.phone) + ' / ' + (str(telefon) or 'Kein Telefon') + '<br>Mobilenummer: ' + str(contact.mobile_no) + ' / ' + (str(mobile) or 'Keine Mobilenummer') + '<br>Geburtsdatum: ' + str(contact.geburtsdatum) + ' / ' + (str(geburtsdatum) or 'Kein Geburtsdatum')

    assign_to = frappe.get_doc("Einstellungen").auto_assign
    for assign in assign_to:
        if assign.dokument_aufgabe == "Anfrage - Mutation Mitglied":
            assign_to = assign.user
            break

    return {'abweichungen': abweichungen, 'assign_to': assign_to}

@frappe.whitelist()
def assign_mitglied_anlage():
    assign_to = frappe.get_doc("Einstellungen").auto_assign
    for assign in assign_to:
        if assign.dokument_aufgabe == "Anfrage - Neu Anlage Mitglied":
            assign_to = assign.user
            break
    return assign_to

@frappe.whitelist()
def create_zeiten_uebersicht(dt, name):
    alle_zeiten = get_zeiten_uebersicht(dt, name)
    if alle_zeiten:
        html = '<div style="width: 50%;"><table style="width: 100%;" class="table-striped"><tr><th>Datum</th><th>Stunden</th><th>Timesheet</th><th>Bearbeiten</th></tr>'
        for zeit in alle_zeiten:
            html += '<tr><td>' + get_datetime_str(zeit.from_time).split(" ")[0] + '</td><td>' + str(zeit.hours) + '</td><td>' + zeit.parent + '</td><td><a data-referenz="' + zeit.parent + '" data-funktion="open_ts"><i class="fa fa-edit"></i></a></td></tr>'
        html += '</table></div>'
        return html
    else:
        return False

@frappe.whitelist()
def kontaktdaten_suchen(vorname='', nachname='', strasse='', adress_zusatz='', plz='', ort='', kanton='', mail='', telefon='', mobile='', geburtsdatum=''):
    # Adressen
    go_adressen_query = False
    if strasse:
        strasse = """ AND `address_line1` LIKE '%{strasse}%'""".format(strasse=strasse)
        go_adressen_query = True
    if adress_zusatz:
        adress_zusatz = """ AND `address_line2` LIKE '%{adress_zusatz}%'""".format(adress_zusatz=adress_zusatz)
        go_adressen_query = True
    if plz:
        plz = """ AND `plz` LIKE '%{plz}%'""".format(plz=plz)
        go_adressen_query = True
    if ort:
        ort = """ AND `city` LIKE '%{ort}%'""".format(ort=ort)
        go_adressen_query = True
    if kanton:
        kanton = """ AND `kanton` LIKE '%{kanton}%'""".format(kanton=kanton)
        go_adressen_query = True
    if go_adressen_query:
        adressen_query = strasse + adress_zusatz + plz + ort + kanton
        adressen_query = adressen_query.replace(" AND", "WHERE", 1)
        adressen_query = """SELECT `name` FROM `tabAddress` {adressen_query}""".format(adressen_query=adressen_query)
        _alle_adressen = frappe.db.sql(adressen_query, as_dict=True)
        alle_adressen = []
        for adresse in _alle_adressen:
            adressen_container = {}
            adressen_container['adresse'] = frappe.db.sql("""SELECT * FROM `tabAddress` WHERE `name` = '{adresse}'""".format(adresse=adresse.name), as_dict=True)
            adressen_container['kunde'] = frappe.db.sql("""SELECT `link_name` FROM `tabDynamic Link` WHERE `parenttype` = 'Address' AND `link_doctype` = 'Customer' AND `parent` = '{adresse}'""".format(adresse=adresse.name), as_dict=True)
            if len(adressen_container['kunde']) > 0:
                alle_adressen.append(adressen_container)
    else:
        adressen_query = ''
        alle_adressen = []
    # /Adressen

    # Kontakte
    go_kontakte_query = False
    if vorname:
        vorname = """ AND `first_name` LIKE '%{vorname}%'""".format(vorname=vorname)
        go_kontakte_query = True
    if nachname:
        nachname = """ AND `last_name` LIKE '%{nachname}%'""".format(nachname=nachname)
        go_kontakte_query = True
    if mail:
        mail = """ AND `email_id` LIKE '%{mail}%'""".format(mail=mail)
        go_kontakte_query = True
    if geburtsdatum:
        geburtsdatum = """ AND `geburtsdatum` LIKE '%{geburtsdatum}%'""".format(geburtsdatum=geburtsdatum)
        go_kontakte_query = True
    if mobile:
        mobile = """ AND `mobile_no` LIKE '%{mobile}%'""".format(mobile=mobile)
        go_kontakte_query = True
    if telefon:
        telefon = """ AND `phone` LIKE '%{telefon}%'""".format(telefon=telefon)
        go_kontakte_query = True
    if go_kontakte_query:
        kontakte_query = vorname + nachname + mail + geburtsdatum + mobile + telefon
        kontakte_query = kontakte_query.replace(" AND", "WHERE", 1)
        kontakte_query = """SELECT `name` FROM `tabContact` {kontakte_query}""".format(kontakte_query=kontakte_query)
        _alle_kontakte = frappe.db.sql(kontakte_query, as_dict=True)
        alle_kontakte = []
        for kontakt in _alle_kontakte:
            kontakt_container = {}
            kontakt_container['kontakt'] = frappe.db.sql("""SELECT * FROM `tabContact` WHERE `name` = '{kontakt}'""".format(kontakt=kontakt.name), as_dict=True)
            kontakt_container['kunde'] = frappe.db.sql("""SELECT `link_name` FROM `tabDynamic Link` WHERE `parenttype` = 'Contact' AND `link_doctype` = 'Customer' AND `parent` = '{kontakt}'""".format(kontakt=kontakt.name), as_dict=True)
            if len(kontakt_container['kunde']) > 0:
                alle_kontakte.append(kontakt_container)
    else:
        kontakte_query = ''
        alle_kontakte = []
    # /Kontakte

    # Full Matches
    if go_kontakte_query and go_adressen_query:
        alle_kunden = frappe.db.sql("""
                                        SELECT DISTINCT `link_name` FROM `tabDynamic Link`
                                            WHERE `link_doctype` = 'Customer'
                                                AND (
                                                    (`parenttype` = 'Address' AND `parent` IN ({adressen_query}))
                                                OR
                                                    (`parenttype` = 'Contact' AND `parent` IN ({kontakte_query}))
                                                )
                                    """.format(adressen_query=adressen_query, kontakte_query=kontakte_query), as_dict=True)
        full_matches = []
        for kunde in alle_kunden:
            kunden_container = {}
            kunden_container['kunde'] = kunde.link_name
            kunden_container['adressen'] = frappe.db.sql("""
                                                            SELECT * FROM `tabAddress`
                                                                WHERE `name` IN ({adressen_query})
                                                                AND `name` IN (
                                                                    SELECT `parent` FROM `tabDynamic Link` WHERE `parenttype` = 'Address' AND `link_name` = '{kunde}'
                                                                )
                                                        """.format(adressen_query=adressen_query, kunde=kunde.link_name), as_dict=True)
            kunden_container['kontakte'] = frappe.db.sql("""
                                                            SELECT * FROM `tabContact`
                                                                WHERE `name` IN ({kontakte_query})
                                                                AND `name` IN (
                                                                    SELECT `parent` FROM `tabDynamic Link` WHERE `parenttype` = 'Contact' AND `link_name` = '{kunde}'
                                                                )
                                                        """.format(kontakte_query=kontakte_query, kunde=kunde.link_name), as_dict=True)
            if len(kunden_container['adressen']) > 0 and len(kunden_container['kontakte']) > 0:
                full_matches.append(kunden_container)
    else:
        full_matches = []
    # /Full Matches

    return {
        'full_matches': full_matches,
        'alle_kontakte': alle_kontakte,
        'alle_adressen': alle_adressen
    }

@frappe.whitelist()
def get_kunden_data(kunde, adresse, kontakt):
    kunde = frappe.get_doc("Customer", kunde)
    adresse = frappe.get_doc("Address", adresse)
    kontakt = frappe.get_doc("Contact", kontakt)

    html = '<div><h3>Kunde:</h3><h4>'
    if kunde.customer_name:
        html += kunde.customer_name
    html += '</h4><div class="row"><div class="col-sm-6"><p>'
    if kontakt.first_name and kontakt.last_name:
        html += kontakt.first_name + " " + kontakt.last_name + "<br>"
    if kontakt.email_id:
        html += kontakt.email_id + "<br>"
    if kontakt.phone:
        html += kontakt.phone + "<br>"
    if kontakt.mobile_no:
        html += kontakt.mobile_no
    html += '</p></div><div class="col-sm-6"><p>'
    if adresse.address_line1:
        html += adresse.address_line1 + "<br>"
    if adresse.address_line2:
        html += adresse.address_line2 + '<br>'
    if adresse.plz:
        html += adresse.plz
    if adresse.city:
        html += " " + adresse.city
    if adresse.kanton:
        html += " " + adresse.kanton
    html += '</p></div></div>'

    return html

@frappe.whitelist()
def get_angehoerige_data(ang, adresse, kontakt):
    ang = frappe.get_doc("Customer", ang)
    adresse = frappe.get_doc("Address", adresse)
    kontakt = frappe.get_doc("Contact", kontakt)

    html = '<div><h3>Angehörige:</h3><h4>'
    if ang.customer_name:
        html += ang.customer_name
    html += '</h4><div class="row"><div class="col-sm-6"><p>'
    if kontakt.first_name and kontakt.last_name:
        html += kontakt.first_name + " " + kontakt.last_name + "<br>"
    if kontakt.email_id:
        html += kontakt.email_id + "<br>"
    if kontakt.phone:
        html += kontakt.phone + "<br>"
    if kontakt.mobile_no:
        html += kontakt.mobile_no
    html += '</p></div><div class="col-sm-6"><p>'
    if adresse.address_line1:
        html += adresse.address_line1 + "<br>"
    if adresse.address_line2:
        html += adresse.address_line2 + '<br>'
    if adresse.plz:
        html += adresse.plz
    if adresse.city:
        html += " " + adresse.city
    if adresse.kanton:
        html += " " + adresse.kanton
    html += '</p></div></div>'

    return html

@frappe.whitelist()
def get_rsv_data(rsv, adresse, kontakt):
    rsv = frappe.get_doc("Customer", rsv)
    adresse = frappe.get_doc("Address", adresse)
    kontakt = frappe.get_doc("Contact", kontakt)

    html = '<div><h3>Auftraggeber:</h3><h4>'
    if rsv.customer_name:
        html += rsv.customer_name
    html += '</h4><div class="row"><div class="col-sm-6"><p>'
    if kontakt.first_name and kontakt.last_name:
        html += kontakt.first_name + " " + kontakt.last_name + "<br>"
    if kontakt.email_id:
        html += kontakt.email_id + "<br>"
    if kontakt.phone:
        html += kontakt.phone + "<br>"
    if kontakt.mobile_no:
        html += kontakt.mobile_no
    html += '</p></div><div class="col-sm-6"><p>'
    if adresse.address_line1:
        html += adresse.address_line1 + "<br>"
    if adresse.address_line2:
        html += adresse.address_line2 + '<br>'
    if adresse.plz:
        html += adresse.plz
    if adresse.city:
        html += " " + adresse.city
    if adresse.kanton:
        html += " " + adresse.kanton
    html += '</p></div></div>'

    return html
