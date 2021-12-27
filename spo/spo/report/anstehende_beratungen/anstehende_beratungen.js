// Copyright (c) 2016, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Anstehende Beratungen"] = {
    "filters": [
        {
            "fieldname": "start",
            "label": __("Von"),
            "fieldtype": "Datetime",
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), +1)
        },
        {
            "fieldname": "end",
            "label": __("Bis"),
            "fieldtype": "Datetime",
            "default": frappe.add_hours(frappe.datetime.add_days(frappe.datetime.get_today(), +1), +24)
        },
        {
            "fieldname": "user",
            "label": __("BeraterIn"),
            "fieldtype": "Link",
            "options": "Beraterzuweisung",
            "reqd": 1
        }
    ]
};
