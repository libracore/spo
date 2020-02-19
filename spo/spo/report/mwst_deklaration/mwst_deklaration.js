// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["MwSt Deklaration"] = {
	"filters": [
		{
			fieldname:"from_date",
			label: __("From date"),
			fieldtype: "Date",
			default: function() {
                var month = new Date().getMonth() + 1;                
                if (month < 4) { return new Date(new Date().getFullYear() - 1, 9, 1); } 
                else if (month < 7) { return new Date(new Date().getFullYear(), 0, 1); } 
                else if (month < 10) { return new Date(new Date().getFullYear(), 3, 1); }
                else { return new Date(new Date().getFullYear(), 6, 1); }
            },
			reqd: 1,
		},
        {
			fieldname:"to_date",
			label: __("To date"),
			fieldtype: "Date",
			default: function() {
                var month = new Date().getMonth() + 1;                
                if (month < 4) { return new Date(new Date().getFullYear() - 1, 11, 31); } 
                else if (month < 7) { return new Date(new Date().getFullYear(), 2, 31); } 
                else if (month < 10) { return new Date(new Date().getFullYear(), 5, 30); }
                else { return new Date(new Date().getFullYear(), 8, 30); }
            },
			reqd: 1,
		}
	]
};
