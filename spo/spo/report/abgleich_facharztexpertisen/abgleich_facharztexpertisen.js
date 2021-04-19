// Copyright (c) 2016, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Abgleich Facharztexpertisen"] = {
	"filters": [
        {
			"fieldname": "abgleich_ab",
			"label": __("Abgleich ab"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": new Date()
		}
	]
};
