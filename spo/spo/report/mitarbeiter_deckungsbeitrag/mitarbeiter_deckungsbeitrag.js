// Copyright (c) 2016, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Mitarbeiter Deckungsbeitrag"] = {
	"filters": [
        {
			"fieldname": "from_date",
			"label": __("Von"),
			"fieldtype": "Date",
			"reqd": 1
		},
        {
			"fieldname": "to_date",
			"label": __("Bis"),
			"fieldtype": "Date",
			"reqd": 1
		}
	]
};
