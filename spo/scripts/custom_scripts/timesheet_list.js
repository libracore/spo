frappe.listview_settings['Timesheet'] = {
    onload: function(listview) {
        listview.page.add_menu_item( __("Sollzeit Buchung"), function() {
			frappe.prompt([
				{'fieldname': 'time', 'fieldtype': 'Time', 'label': 'Zeitpunkt', 'reqd': 1}  
			],
			function(values){
				console.log(values);
				sollzeit(values.time);
			},
			'Sollzeit Buchung',
			'Erfassen'
			)
		});
    }
}

function sollzeit(time) {
	frappe.call({
		method: "spo.utils.timesheet_handlings.sollzeit",
		args:{
			"user": frappe.user.name,
			"time": time
		},
		callback: function(r)
		{
			if (r.message == 'ok') {
				frappe.msgprint("Die Sollzeit Buchung wurde erfasst.");
			}
		}
	});
}