// Copyright (c) 2016, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Mitgliederstatistik"] = {
    "filters": [
        {
            "fieldname": "von",
            "label": __("Von"),
            "fieldtype": "Date",
            "reqd": 1
        },
        {
            "fieldname": "bis",
            "label": __("Bis"),
            "fieldtype": "Date",
            "reqd": 1
        },
        {
            "fieldname": "einblenden",
            "label": __("In Grafik einblenden"),
            "fieldtype": "Data"
        },
        {
            "fieldname": "chart_type",
            "label": __("Grafik Typ"),
            "fieldtype": "Select",
            "options": "Bar\nLine",
            "default": "Bar"
        }
    ]
};
