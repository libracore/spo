// Copyright (c) 2016, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Spendenübersicht"] = {
    "filters": [
        {
            "fieldname": "ansicht",
            "label": __("Ansicht"),
            "fieldtype": "Select",
            "reqd": 1,
            "options": "5 Jahre jährlich\n1 Jahr monatlich"
        },
        {
            "fieldname": "bezugsjahr",
            "label": __("Bezugsjahr"),
            "fieldtype": "Int",
            "reqd": 0
        }
    ]
};
