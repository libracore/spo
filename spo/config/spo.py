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
					"name": "Anfrage",
					"label": "Anfragen",
					"description": _("Mandats und oder sonstige Anfragen"),
				},
				{
					"type": "doctype",
					"name": "Mandat",
					"label": "Mandate",
					"description": _("Führendes Mandats-Dokument"),
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
					"name": "Vollmacht",
					"label": "Vollmacht",
					"description": _("Vollmacht"),
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
				}
			]
		}
	]
