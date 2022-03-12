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
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -12)
		},
        {
			"fieldname": "abgleich_bis",
			"label": __("Abgleich bis"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
        {
			"fieldname": "nur_offene",
			"label": __("Nur offene"),
			"fieldtype": "Check",
			"default": 1
		}
	]
};
