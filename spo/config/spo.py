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
					"label": "Telefon Triage",
					"description": _("Telefon Triage"),
				},
				{
					"type": "doctype",
					"name": "Anfrage",
					"label": "Anfragen",
					"description": _("Mandats und oder sonstige Anfragen"),
				},
				{
					"type": "doctype",
					"name": "Mandat",
					"label": "Mandate",
					"description": _("Führendes Mandats-Dokument"),
				},
				{
					"type": "report",
					"name": "Alle Mandate in Arbeit",
					"label": "Alle Mandate in Arbeit",
					"description": _("Alle Mandate in Arbeit"),
					"doctype": "Telefon Triage",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Address And Contacts",
					"label": "Adressliste",
					"description": _("Adressliste"),
					#"doctype": "Telefon Triage",
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
					"label": "Mitgliedschaften",
					"description": _("SPO Mitgliedschaften"),
				},
				{
					"type": "doctype",
					"name": "Customer",
					"label": "Kunden",
					"description": _("Customers"),
				},
				{
					"type": "doctype",
					"label": "Rechnungen",
					"name": "Sales Invoice",
					"description": _("Sales Invoice"),
				},
				{
					"type": "doctype",
					"label": "Rechnungslauf",
					"name": "Mitglieder Rechnungslauf",
					"description": _("Mitglieder Rechnungslauf"),
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
					"label": "Anforderung Patientendossier",
					"description": _("Anforderung Patientendossier"),
				},
				{
					"type": "doctype",
					"name": "Medizinischer Bericht",
					"label": "Medizinischer Bericht",
					"description": _("Medizinischer Bericht"),
				},
				{
					"type": "doctype",
					"name": "Triage",
					"label": "Triage",
					"description": _("Triage"),
				},
				{
					"type": "doctype",
					"name": "Vollmacht",
					"label": "Vollmacht",
					"description": _("Vollmacht"),
				},
				{
					"type": "doctype",
					"name": "Abschlussbericht",
					"label": "Abschlussbericht",
					"description": _("Abschlussbericht"),
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
					"label": "Defaults",
					"description": _("Standard Einstellungen"),
				},
				{
					"type": "doctype",
					"name": "SPO Textbausteine",
					"label": "Textbausteine",
					"description": _("Benutzerspezifische Textbausteine"),
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
					"label": "Zeiterfassungs Manager",
					"description": _("Zeiterfassungs Manager"),
				}
			]
		}
	]
