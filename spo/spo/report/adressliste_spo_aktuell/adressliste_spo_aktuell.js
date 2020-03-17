// Copyright (c) 2016, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Adressliste SPO Aktuell"] = {
	"filters": [
		{
			"fieldname": "customer_group",
			"label": __("Customer Group"),
			"fieldtype": "Select",
			"options": ["Mitglied", "Newsletter Abo"]
		}
	]
};
