// Copyright (c) 2016, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["SPO Fallbibliothek"] = {
	"filters": [

	],
    get_datatable_options(options) {
		delete options['cellHeight']
		// change datatable options
		return Object.assign(options, {
			dynamicRowHeight: true
		});
	},
	onload: function(report) {
		report.page.add_inner_button(__("Extend Row"), function() {
			$(".dt-row.vrow").each(function(){
                $(this).addClass("extend-row");
            });
		});
	},
    "formatter": function (value, row, column, data, default_formatter) {
       value = default_formatter(value, row, column, data);
       if (column.id == "anonym") {
            if (value.includes("MEB-")) {
                value = "<span onclick=" + '"goto_med_ber(' + "'" + value + "'" + ');"' + ">" + value + "</span>";
            }
            if (value.includes("TRI-")) {
                value = "<span onclick=" + '"goto_triage(' + "'" + value + "'" + ');"' + ">" + value + "</span>";
            }
       }
       return value;
    }
};

function goto_triage(triage) {
    frappe.call({
        "method": "spo.spo.doctype.triage_anonym.triage_anonym.create_view",
        "args": {
            "triage": triage
        },
        "async": false,
        "callback": function(response) {
            frappe.set_route("Form", "Triage Anonym", response.message);
        }
    });
}

function goto_med_ber(med_ber) {
    frappe.call({
        "method": "spo.spo.doctype.med_ber_anonym.med_ber_anonym.create_view",
        "args": {
            "med_ber": med_ber
        },
        "async": false,
        "callback": function(response) {
            frappe.set_route("Form", "Med Ber Anonym", response.message);
        }
    });
}