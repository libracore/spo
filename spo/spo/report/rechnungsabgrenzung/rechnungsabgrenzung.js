// Copyright (c) 2016, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Rechnungsabgrenzung"] = {
	"filters": [
		{
			"reqd": 1,
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": 'Gönnerverein'
		},
		{
			'fieldname': "stichtag",
			'label': __("Stichtag (Stand heute)"),
			'fieldtype': "Date",
			'default': frappe.datetime.year_end(frappe.datetime.get_today()),
			'reqd': 1
		}
	]
};
