// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mandat', {
	refresh: function(frm) {
		//erstellen des Dashboards, wenn ein Mitglied eingetragen ist
		if (frm.doc.mitglied) {
			update_dashboard(frm);
		}
	}
});


function update_dashboard(frm) {
	frappe.call({
		"method": "spo.spo.doctype.mandat.mandat.get_dashboard_data",
		"args": {
			"mitglied": frm.doc.mitglied
		},
		"async": false,
		"callback": function(response) {
			var query = response.message;
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
						values: [query.callcenter_verwendet, query.callcenter_limit - query.callcenter_verwendet]
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