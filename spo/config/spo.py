from __future__ import unicode_literals
from frappe import _

def get_data():
    return [
        {
            "label": _("Mandatsverwaltung"),
            "icon": "fa fa-cog",
            "items": [
                {
                    "type": "doctype",
                    "name": "Telefon Triage",
                    "label": _("Telefon Triage"),
                    "description": _("Telefon Triage")
                },
                {
                    "type": "doctype",
                    "name": "Anfrage",
                    "label": _("Anfragen"),
                    "description": _("Mandats und oder sonstige Anfragen")
                },
                {
                    "type": "doctype",
                    "name": "Mandat",
                    "label": _("Mandate"),
                    "description": _("Führendes Mandats-Dokument")
                },
                {
                    "type": "doctype",
                    "name": "Meldestelle",
                    "label": _("Meldestelle"),
                    "description": _("Führendes Meldestelle-Dokument")
                },
                {
                    "type": "report",
                    "name": "Alle Mandate in Arbeit",
                    "label": _("Alle Mandate in Arbeit"),
                    "description": _("Alle Mandate in Arbeit"),
                    "doctype": "Telefon Triage",
                    "is_query_report": True
                },
                {
                    "type": "report",
                    "name": "Alle Anfragen",
                    "label": _("Alle Anfragen"),
                    "description": _("Anfragen"),
                    "doctype": "Anfrage",
                    "is_query_report": True
                },
                {
                    "type": "report",
                    "name": "SPO Adressliste",
                    "label": _("Adressliste"),
                    "description": _("Adressliste"),
                    "is_query_report": True
                },
                {
                    "type": "report",
                    "name": "SPO Fallbibliothek",
                    "label": _("Fallbibliothek"),
                    "description": _("Fallbibliothek"),
                    "is_query_report": True
                }
            ]
        },
        {
            "label": _("Mitgliederverwaltung"),
            "icon": "fa fa-cog",
            "items": [
                {
                    "type": "doctype",
                    "name": "Mitgliedschaft",
                    "label": _("Mitgliedschaften"),
                    "description": _("SPO Mitgliedschaften")
                },
                {
                    "type": "doctype",
                    "name": "Customer",
                    "label": _("Kunden"),
                    "description": _("Customers")
                },
                {
                    "type": "doctype",
                    "label": _("Rechnungen"),
                    "name": "Sales Invoice",
                    "description": _("Sales Invoice")
                },
                {
                    "type": "doctype",
                    "label": _("Rechnungslauf"),
                    "name": "Mitglieder Rechnungslauf",
                    "description": _("Mitglieder Rechnungslauf")
                },
                {
                    "type": "report",
                    "name": "Adressliste SPO Aktuell",
                    "label": _("Adressliste SPO Aktuell"),
                    "description": _("Adressliste SPO Aktuell"),
                    "doctype": "Contact",
                    "is_query_report": True
                },
                {
                    "type": "report",
                    "name": "Spendenübersicht",
                    "label": _("Spendenübersicht"),
                    "description": _("Spendenübersicht"),
                    "doctype": "Payment Entry",
                    "is_query_report": True
                },
                {
                    "type": "report",
                    "name": "Aktive Mitglieder per Stichtag",
                    "label": _("Aktive Mitglieder per Stichtag"),
                    "description": _("Aktive Mitglieder per Stichtag"),
                    "doctype": "Mitgliedschaft",
                    "is_query_report": True
                },
                {
                    "type": "report",
                    "name": "Demographie Mitglieder",
                    "label": _("Demographie Mitglieder"),
                    "description": _("Demographie Mitglieder"),
                    "doctype": "Mitgliedschaft",
                    "is_query_report": True
                },
                {
                    "type": "report",
                    "name": "Mitgliederstatistik",
                    "label": _("Mitgliederstatistik"),
                    "description": _("Mitgliederstatistik"),
                    "doctype": "Mitgliedschaft",
                    "is_query_report": True
                },
                {
                    "type": "doctype",
                    "label": _("Customer Deactivation Log"),
                    "name": "Customer Deactivation Log",
                    "description": _("Customer Deactivation Log")
                }
            ]
        },
        {
            "label": _("Protokolle & Checklisten"),
            "icon": "fa fa-cog",
            "items": [
                {
                    "type": "doctype",
                    "name": "Anforderung Patientendossier",
                    "label": _("Anforderung Patientendossier"),
                    "description": _("Anforderung Patientendossier")
                },
                {
                    "type": "doctype",
                    "name": "Medizinischer Bericht",
                    "label": _("Medizinischer Bericht"),
                    "description": _("Medizinischer Bericht")
                },
                {
                    "type": "doctype",
                    "name": "Triage",
                    "label": _("Triage"),
                    "description": _("Triage")
                },
                {
                    "type": "doctype",
                    "name": "Vollmacht",
                    "label": _("Vollmacht"),
                    "description": _("Vollmacht")
                },
                {
                    "type": "doctype",
                    "name": "Abschlussbericht",
                    "label": _("Abschlussbericht"),
                    "description": _("Abschlussbericht")
                },
                {
                    "type": "doctype",
                    "name": "Freies Schreiben",
                    "label": _("Freies Schreiben"),
                    "description": _("Freies Schreiben")
                },
                {
                    "type": "doctype",
                    "name": "Facharzt Bericht",
                    "label": _("Facharzt Bericht"),
                    "description": _("Facharzt Bericht")
                }
            ]
        },
        {
            "label": _("Einstellungen"),
            "icon": "fa fa-cog",
            "items": [
                {
                    "type": "doctype",
                    "name": "Einstellungen",
                    "label": _("Defaults"),
                    "description": _("Standard Einstellungen")
                },
                {
                    "type": "doctype",
                    "name": "SPO Textbausteine",
                    "label": _("Textbausteine"),
                    "description": _("Benutzerspezifische Textbausteine")
                },
                {
                    "type": "doctype",
                    "name": "Ombudsstellen Partner",
                    "label": _("Ombudsstellen Partner"),
                    "description": _("Ombudsstellen Partner")
                }
            ]
        },
        {
            "label": _("Zeiterfassung"),
            "icon": "fa fa-cog",
            "items": [
                {
                    "type": "doctype",
                    "name": "Zeiterfassung",
                    "label": _("Zeiterfassungs Manager"),
                    "description": _("Zeiterfassungs Manager")
                },
                {
                    "type": "report",
                    "name": "Timesheets Jahresrapport",
                    "label": _("Timesheets Jahresrapport"),
                    "description": _("Timesheets Jahresrapport"),
                    "is_query_report": True
                },
                {
                    "type": "report",
                    "name": "Mitarbeiter Deckungsbeitrag",
                    "label": _("Mitarbeiter Deckungsbeitrag"),
                    "description": _("Mitarbeiter Deckungsbeitrag"),
                    "is_query_report": True
                }
            ]
        },
        {
            "label": _("Kreditoren"),
            "icon": "fa fa-cog",
            "items": [
                {
                    "type": "doctype",
                    "name": "Supplier",
                    "label": _("Supplier"),
                    "description": _("Supplier")
                },
                {
                    "type": "doctype",
                    "name": "Purchase Invoice",
                    "label": _("Purchase Invoice"),
                    "description": _("Purchase Invoice")
                },
                {
                    "type": "doctype",
                    "name": "Payment Proposal",
                    "label": _("Payment Proposal"),
                    "description": _("Payment Proposal")
                },
                {
                       "type": "page",
                       "name": "bank_wizard",
                       "label": _("Bank Wizard"),
                       "description": _("Bank Wizard")
                }
            ]
        },
        {
            "label": _("Buchhaltung"),
            "icon": "fa fa-cog",
            "items": [
                {
                    "type": "report",
                    "name": "MwSt Deklaration",
                    "label": _("MwSt Deklaration"),
                    "doctype": "GL Entry",
                    "is_query_report": True
                },
                {
                    "type": "report",
                    "name": "MwSt Deklaration 2024",
                    "label": _("MwSt Deklaration 2024"),
                    "doctype": "GL Entry",
                    "is_query_report": True
                },
                {
                    "type": "report",
                    "name": "General Ledger",
                    "label": _("General Ledger"),
                    "doctype": "GL Entry",
                    "is_query_report": True
                },
                {
                    "type": "report",
                    "name": "Rechnungsabgrenzung",
                    "label": _("Rechnungsabgrenzung"),
                    "doctype": "Sales Invoice",
                    "is_query_report": True
                },
                {
                    "type": "report",
                    "name": "Abgleich Facharztexpertisen",
                    "label": _("Abgleich Facharztexpertisen"),
                    "doctype": "Mandat",
                    "is_query_report": True
                }
            ]
        },
        {
            "label": _("Onlinetermin"),
            "icon": "fa fa-cog",
            "items": [
                {
                    "type": "doctype",
                    "name": "Beratungsplanung",
                    "label": _("Beratungsplanung"),
                    "description": _("Beratungsplanung")
                },
                {
                    "type": "doctype",
                    "name": "Beratungsslot",
                    "label": _("Beratungsslot"),
                    "description": _("Beratungsslot")
                },
                {
                    "type": "doctype",
                    "name": "Beraterzuweisung",
                    "label": _("Beraterzuweisung"),
                    "description": _("Beraterzuweisung")
                },
                {
                    "type": "doctype",
                    "name": "Einstellungen Onlinetermin",
                    "label": _("Einstellungen Onlinetermin"),
                    "description": _("Einstellungen Onlinetermin")
                },
                {
                    "type": "doctype",
                    "name": "Onlinetermin Access Log",
                    "label": _("Onlinetermin Access Log"),
                    "description": _("Onlinetermin Access Log")
                },
                {
                    "type": "report",
                    "name": "Anstehende Beratungen",
                    "label": _("Anstehende Beratungen"),
                    "doctype": "Beratungsslot",
                    "is_query_report": True
                },
                {
                    "type": "report",
                    "name": "Unbezahlte Beratungen",
                    "label": _("Unbezahlte Beratungen"),
                    "doctype": "Beratungsslot",
                    "is_query_report": True
                },
            ]
        }
    ]
