// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mandat', {
	refresh: function(frm) {
		/* //erstellen des Dashboards, wenn ein Mitglied eingetragen ist
		if (frm.doc.mitglied) {
			update_dashboard(frm);
		} */
		//erstellen des Dashboards
		update_dashboard(frm);
		
		// timer action icon
		cur_frm.page.add_action_icon(__("fa fa-history"), function() {
			timesheet_handling(frm);
		});
	}
});


function update_dashboard(frm) {
	frappe.call({
		"method": "spo.spo.doctype.mandat.mandat.get_dashboard_data",
		"args": {
			"mitglied": frm.doc.mitglied,
			"anfrage": frm.doc.anfragen,
			"mandat": frm.doc.name
		},
		"async": false,
		"callback": function(response) {
			var query = response.message;
			var max_aufwand = query.callcenter_limit;
			if (frm.doc.max_aufwand > 0) {
				max_aufwand = frm.doc.max_aufwand;
			}
			//Limits
			var _colors = ['#d40000', '#00b000'];
			if (query.callcenter_verwendet == 0) {
				_colors = ['#00b000', '#d40000'];
			}
			let limit_chart = new frappe.Chart( "#limit", { // or DOM element
				data: {
				labels: ["Verwendet", "Ausstehend"],

				datasets: [
					{
						values: [query.callcenter_verwendet, max_aufwand - query.callcenter_verwendet]
					}
				],

				},
				title: "Zeitauswertung (in min)",
				type: 'percentage', // or 'bar', 'line', 'pie', 'percentage'
				colors: _colors,
				barOptions: {
					height: 20,          // default: 20
					depth: 2             // default: 2
				}
			});
		}
	});
}

function timesheet_handling(frm) {
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