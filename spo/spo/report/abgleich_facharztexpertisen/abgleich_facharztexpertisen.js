// Copyright (c) 2016-2022, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Abgleich Facharztexpertisen"] = {
	"filters": [
        {
			"fieldname": "abgleich_ab",
			"label": __("Abgleich ab"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": new Date(2000, 0, 1)
		},
        {
			"fieldname": "abgleich_bis",
			"label": __("Abgleich bis"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": new Date()
		},
        {
			"fieldname": "nur_offene",
			"label": __("Nur offene"),
			"fieldtype": "Check",
			"default": 1
		}
	]
};
