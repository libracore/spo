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
	}
};
