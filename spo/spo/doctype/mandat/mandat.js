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
		"method": "spo.spo.doctype.anfrage.anfrage.get_dashboard_data",
		"args": {
			"mitglied": frm.doc.mitglied
		},
		"async": false,
		"callback": function(response) {
			var query = response.message;
			//Chart
			let chart = new Chart( "#chart", { // or DOM element
				data: {
				labels: ["Letztes Jahr", "YTD", "Q1", "Q2", "Q3", "Q4"],
				
				datasets: [
					{
						name: "Als Mitglied", chartType: 'bar',
						values: [query.m_last_year, query.m_ytd, query.m_q1, query.m_q2, query.m_q3, query.m_q4]
					},
					{
						name: "Ohne<br>Mitgliedschaft", chartType: 'bar',
						values: [query.o_last_year, query.o_ytd, query.o_q1, query.o_q2, query.o_q3, query.o_q4]
					},
					{
						name: "&Oslash;", chartType: 'line',
						values: [(query.m_last_year + query.o_last_year) / 2, (query.m_ytd + query.o_ytd) / 2, (query.m_q1 + query.o_q1) / 2, (query.m_q2 + query.o_q2) / 2, (query.m_q3 + query.o_q3) / 2, (query.m_q4 + query.o_q4) / 2]
					},
					{
						name: "Total", chartType: 'line',
						values: [(query.m_last_year + query.o_last_year), (query.m_ytd + query.o_ytd), (query.m_q1 + query.o_q1), (query.m_q2 + query.o_q2), (query.m_q3 + query.o_q3), (query.m_q4 + query.o_q4)]
					}
				],

				yMarkers: [{ label: "Mittelwert", value: (query.m_last_year + query.o_last_year + query.m_ytd + query.o_ytd + query.m_q1 + query.o_q1 + query.m_q2 + query.o_q2 + query.m_q3 + query.o_q3 + query.m_q4 + query.o_q4) / 12,
					options: { labelPos: 'left' }}],
				/*yRegions: [{ label: "Region", start: -10, end: 50,
					options: { labelPos: 'right' }}]
				*/},

				
				type: 'axis-mixed', // or 'bar', 'line', 'pie', 'percentage'
				height: 180,
				colors: ['#00b000', '#d40000', 'light-blue', 'blue'],

				tooltipOptions: {
					formatTooltipX: d => (d + '').toUpperCase(),
					formatTooltipY: d => d + ' min',
				}
			});
			
			//Limits
			var _colors = ['#d40000', '#00b000'];
			if (query.callcenter_verwendet == 0) {
				_colors = ['#00b000', '#d40000'];
			}
			let limit_chart = new Chart( "#limit", { // or DOM element
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
					height: 1,          // default: 20
					depth: 1             // default: 2
				}
			});
		}
	});
}