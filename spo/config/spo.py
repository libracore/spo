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
					"description": _("Mandats und oder sonstige Anfragen"),
				}
			]
		}
	]
