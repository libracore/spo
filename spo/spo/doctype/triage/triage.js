// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Triage', {
	validate: function(frm) {
		frappe.prompt([
			{'fieldname': 'time', 'fieldtype': 'Float', 'label': 'Total Time (in hours)', 'reqd': 1}  
		],
		function(values){
			console.log(frm.doc.doctype);
			frappe.call({
				"method": "spo.utils.timesheet_handlings.handle_timesheet",
				"args": {
					"user": frappe.session.user_email,
					"doctype": frm.doc.doctype,
					"reference": frm.doc.name,
					"time": values.time
				},
				"async": false,
				"callback": function(response) {
					console.log(response);
				}
			});
		},
		'Timesheet Action',
		'Go'
		)
	}
});
