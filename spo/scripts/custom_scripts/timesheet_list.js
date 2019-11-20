frappe.listview_settings['Timesheet'] = {
    onload: function(listview) {
        /* listview.page.add_menu_item( __("Sollzeit Buchung"), function() {
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
		}); */
		listview.page.add_menu_item( __("Erfassung Tagesarbeitszeit"), function() {
			erfassung_tagesarbeitszeit();
		});
		listview.page.add_menu_item( __("Erfassung zusätzliche Pause"), function() {
			erfassung_zusatz_pause();
		});
		listview.page.add_menu_item( __("Restzeit Zuordnung"), function() {
			restzeit_zuordnung();
		});
    }
}

/* function sollzeit(time) {
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
} */

function calc_end_time(start_zeit) {
	var stunden = parseInt(start_zeit.split(":")[0]);
	var end_stunden = stunden + 9;
	var minuten = parseInt(start_zeit.split(":")[1]) + 54;
	while (minuten >= 60) {
		end_stunden = end_stunden + 1;
		minuten = minuten - 60;
	}
	var end_minuten = minuten;
	var end_zeit = end_stunden.toString() + ":" + end_minuten.toString() + ":" + start_zeit.split(":")[2].toString();
	if (end_stunden > 23) {
		end_zeit = "23:59:59";
	}
	
	return end_zeit;
}

function erfassung_tagesarbeitszeit() {
	var start_zeit = frappe.datetime.now_time();
	var end_zeit = calc_end_time(start_zeit);
	frappe.prompt([
			{'fieldname': 'datum', 'fieldtype': 'Date', 'label': 'Datum', 'reqd': 1, 'default': frappe.datetime.get_today()},
			{'fieldname': 'pause', 'fieldtype': 'Time', 'label': 'Zeitpunkt Pause', 'reqd': 1, 'default': '12:00:00'},
			{'fieldname': 'end_time', 'fieldtype': 'Time', 'label': 'Arbeitsende', 'reqd': 1, 'default': end_zeit},
			{'fieldname': 'cb1', 'fieldtype': 'Column Break', 'label': ''},
			{'fieldname': 'start_time', 'fieldtype': 'Time', 'label': 'Arbeitsbeginn', 'reqd': 1, 'default': start_zeit},
			{'fieldname': 'pause_duration', 'fieldtype': 'Float', 'label': 'Pausen Dauer (in h)', 'reqd': 1, 'default': 1.500}
		],
		function(values){
			//console.log(values);
			frappe.call({
				method: "spo.utils.timesheet_handlings.erfassung_tagesarbeitszeit",
				args:{
					"user": frappe.session.user_email,
					"datum": values.datum,
					"start_zeit": values.start_time,
					"pause_start": values.pause,
					"pause_dauer": values.pause_duration,
					"end_zeit": values.end_time
				},
				callback: function(r)
				{
					if (r.message == 'ok') {
						frappe.msgprint("Die Tagesarbeitszeit wurde erfasst.");
					}
				}
			});
		},
		'Erfassung Tagesarbeitszeit',
		'Erfassen'
	);
	var start_time_element = [];
	setTimeout(function(){
		var start_time_element = document.querySelectorAll("[data-fieldname='start_time']");
		start_time_element = start_time_element[start_time_element.length - 1];
		//console.log(start_time_element);
		start_time_element.onchange = function(){
			var end_time = calc_end_time(start_time_element.value);
			var end_time_element = document.querySelectorAll("[data-fieldname='end_time']");
			end_time_element = end_time_element[end_time_element.length - 1];
			end_time_element.value = end_time;
		};
	}, 1000);
	
}

function erfassung_zusatz_pause() {
	var start_zeit = frappe.datetime.now_time();
	frappe.prompt([
			{'fieldname': 'datum', 'fieldtype': 'Date', 'label': 'Datum', 'reqd': 1, 'default': frappe.datetime.get_today()},
			{'fieldname': 'cb1', 'fieldtype': 'Column Break', 'label': ''},
			{'fieldname': 'pause', 'fieldtype': 'Time', 'label': 'Zeitpunkt Pause', 'reqd': 1, 'default': start_zeit},
			{'fieldname': 'cb2', 'fieldtype': 'Column Break', 'label': ''},
			{'fieldname': 'pause_duration', 'fieldtype': 'Float', 'label': 'Pausen Dauer (in h)', 'reqd': 1}
		],
		function(values){
			//console.log(values);
			frappe.call({
				method: "spo.utils.timesheet_handlings.erfassung_zusatz_pause",
				args:{
					"user": frappe.session.user_email,
					"datum": values.datum,
					"start_zeit": values.pause,
					"dauer": values.pause_duration
				},
				callback: function(r)
				{
					if (r.message == 'ok') {
						frappe.msgprint("Die zusätzliche Pause wurde erfasst.");
					}
				}
			});
		},
		'Erfassung Zusatzpause',
		'Erfassen'
	);
}

function restzeit_zuordnung() {
	frappe.call({
		method: "spo.utils.timesheet_handlings.get_restzeit",
		args:{
			"user": frappe.session.user_email
		},
		callback: function(r)
		{
			if (r.message) {
				frappe.prompt([
						{'fieldname': 'datum', 'fieldtype': 'Date', 'label': 'Datum', 'reqd': 1, 'read_only': 1, 'default': frappe.datetime.get_today()},
						{'fieldname': 'sb1', 'fieldtype': 'Section Break', 'label': ''},
						{'fieldname': 'activity', 'fieldtype': 'Link', 'label': 'Activity Type', 'options': 'Activity Type', 'reqd': 1, 'get_query': function() {
								return {
									'filters': [
										["activity_type", "!=", "Arbeitszeit"],
										["activity_type", "!=", "Pause"],
										["activity_type", "!=", "Mandatsarbeit"],
										["activity_type", "!=", "Beratung"]
									]
								}
							}
						},
						{'fieldname': 'cb1', 'fieldtype': 'Column Break', 'label': ''},
						{'fieldname': 'duration', 'fieldtype': 'Float', 'label': 'Dauer (in h)', 'reqd': 1, 'default': parseFloat(r.message)},
						{'fieldname': 'cb2', 'fieldtype': 'Column Break', 'label': ''},
						{'fieldname': 'remark', 'fieldtype': 'Small Text', 'label': 'Bemerkung'}
						
					],
					function(values){
						console.log(values);
						frappe.call({
							method: "spo.utils.timesheet_handlings.restzeit_zuordnung",
							args:{
								"user": frappe.session.user_email,
								"type": values.activity,
								"dauer": values.duration,
								"spo_remark": values.remark
							},
							callback: function(r)
							{
								if (r.message == 'ok') {
									frappe.msgprint("Die Restzeit wurde erfasst.");
								}
							}
						});
					},
					'Restzeit Zuordnung',
					'Zuordnen'
				);
			} else {
				frappe.msgprint("Es gibt Restzeit die noch zugewiesen werden könnte.");
			}
		}
	});
}