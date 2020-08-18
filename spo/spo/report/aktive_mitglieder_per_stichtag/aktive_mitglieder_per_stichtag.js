// Copyright (c) 2016, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Aktive Mitglieder per Stichtag"] = {
	"filters": [
		{
			"fieldname": "stichtag",
			"label": __("Stichtag"),
			"fieldtype": "Date",
			"reqd": 1
			//"default": new Date((new Date()).getFullYear() + "-10-01")
		}
	]
};
