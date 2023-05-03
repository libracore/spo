// Copyright (c) 2016, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Adressliste SPO Aktuell"] = {
    "filters": [
        {
            "fieldname": "base_data",
            "label": __("Datenbasis"),
            "fieldtype": "Select",
            "options": ["Kunden / Mitglieder", "Lieferanten"]
        }
    ]
};
