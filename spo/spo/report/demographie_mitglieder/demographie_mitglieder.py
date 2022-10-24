# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Mitglied"), "fieldname": "mitglied", "fieldtype": "Link", "options": "Customer"},
        {"label": _("Mitgliedschaft"), "fieldname": "mitgliedschaft", "fieldtype": "Link", "options": "Mitgliedschaft"},
        {"label": _("Typ"), "fieldname": "mitgliedschafts_typ", "fieldtype": "Select", "options": "Einzelmitglied\nFamilienmitglied\nPassiv-/Kollektivmitglied\nFreimitglied"},
        {"label": _("Eintrittsdatum"), "fieldname": "eintrittsdatum", "fieldtype": "Date"},
        {"label": _("Anz. Mitgliedschaften"), "fieldname": "anzahl_mitgliedschaften", "fieldtype": "Int", "width": 90},
        {"label": _("Letzte bezahlte Mitgliedschafts Periode"), "fieldname": "letzte_bezahlte_periode", "fieldtype": "Data", "width": 160},
        {"label": _("Anrede"), "fieldname": "anrede", "fieldtype": "Data"},
        {"label": _("Vorname"), "fieldname": "vorname", "fieldtype": "Data"},
        {"label": _("Nachname"), "fieldname": "nachname", "fieldtype": "Data", "width": 110},
        {"label": _("Geburtsdatum"), "fieldname": "geburtsdatum", "fieldtype": "Data"},
        {"label": _("E-Mail"), "fieldname": "email", "fieldtype": "Data"},
        {"label": _("Mobile"), "fieldname": "mobile", "fieldtype": "Data"},
        {"label": _("Strasse"), "fieldname": "strasse", "fieldtype": "Data"},
        {"label": _("PLZ"), "fieldname": "plz", "fieldtype": "Data"},
        {"label": _("Ort"), "fieldname": "ort", "fieldtype": "Data"},
        {"label": _("Kanton"), "fieldname": "kanton", "fieldtype": "Data"},
        {"label": _("Mitgliedschafts Zahlungen"), "fieldname": "mitgliedschafts_zahlungen", "fieldtype": "Currency"},
        {"label": _("Spenden Zahlungen"), "fieldname": "spenden_zahlungen", "fieldtype": "Currency"},
        {"label": _("Spenden Zahlungen Auflistung"), "fieldname": "spenden_auflistung", "fieldtype": "Code"},
        {"label": _("Total Zahlungen"), "fieldname": "zahlungen_total", "fieldtype": "Currency"},
        {"label": _("Letztes Zahlungsdatum"), "fieldname": "letztes_zahlungsdatum", "fieldtype": "Date"}
    ]

def get_data(filters):
    query = """
        SELECT
            `name` AS `mitglied`,
            `aktuelle_mitgliedschaft` AS `mitgliedschaft`,
            `mitgliedschaftstyp` AS `mitgliedschafts_typ`,
            `eintrittsdatum`,
            `anzahl_mitgliedschaften`,
            `letzte_bezahlte_periode`,
            `mitgliedschafts_personen`,
            `multy_entry`,
            `mitgliedschafts_zahlungen`,
            `spenden_zahlungen`,
            `spenden_auflistung`,
            `zahlungen_total`,
            `letztes_zahlungsdatum`
        FROM `tabDemographie Bin`
        WHERE `eintrittsdatum` IS NOT NULL
    """
    
    data = frappe.db.sql(query, as_dict=True)
    return_data = []
    for d in data:
        first_entry = d.copy()
        first_entry['indent'] = 0
        demo_bin = frappe.get_doc("Demographie Bin", d['mitglied'])
        
        for _adresse in demo_bin.adressdaten:
            if _adresse.idx == 1:
                adresse = _adresse
        for _kontakt in demo_bin.kontaktdaten:
            if _kontakt.idx == 1:
                kontakt = _kontakt
        
        if kontakt:
            first_entry['anrede'] = kontakt.anrede
            first_entry['vorname'] = kontakt.vorname
            first_entry['nachname'] = kontakt.nachname
            first_entry['geburtsdatum'] = kontakt.geburtsdatum
            first_entry['email'] = kontakt.mail
            first_entry['mobile'] = kontakt.mobile
        
        if adresse:
            first_entry['strasse'] = adresse.strasse
            first_entry['plz'] = adresse.plz
            first_entry['ort'] = adresse.ort
            first_entry['kanton'] = adresse.kanton
        
        return_data.append(first_entry)
        
        if int(d.multy_entry) == 1:
            for multy_adresse in demo_bin.adressdaten:
                for multy_kontakt in demo_bin.kontaktdaten:
                    if multy_kontakt.idx != 1:
                        following_entries = d.copy()
                        following_entries['indent'] = 1
                        
                        following_entries['anrede'] = multy_kontakt.anrede
                        following_entries['vorname'] = multy_kontakt.vorname
                        following_entries['nachname'] = multy_kontakt.nachname
                        following_entries['geburtsdatum'] = multy_kontakt.geburtsdatum
                        following_entries['email'] = multy_kontakt.mail
                        following_entries['mobile'] = multy_kontakt.mobile
                        
                        following_entries['strasse'] = multy_adresse.strasse
                        following_entries['plz'] = multy_adresse.plz
                        following_entries['ort'] = multy_adresse.ort
                        following_entries['kanton'] = multy_adresse.kanton
                        
                        return_data.append(following_entries)
    
    return return_data
