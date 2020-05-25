frappe.ui.form.on('Employee', {
	validate: function(frm) {
		calc_monatslohn(frm);
		cur_frm.set_value('zeitraum_von', '');
		cur_frm.set_value('zeitraum_bis', '');		
	},
	monatslohn: function(frm) {
		calc_monatslohn(frm);	
	},
	anstellungsgrad: function(frm) {
		calc_monatslohn(frm);	
	},
	onload: function(frm) {
		urlaub(frm);
	},
	zeitraum_von: function(frm) {
		if (cur_frm.doc.zeitraum_bis < cur_frm.doc.zeitraum_von) {
			cur_frm.set_value('zeitraum_bis', cur_frm.doc.zeitraum_von);
		}
		arbeitszeit(frm);
	},
	zeitraum_bis: function(frm) {
		if (cur_frm.doc.zeitraum_bis < cur_frm.doc.zeitraum_von) {
			cur_frm.set_value('zeitraum_bis', cur_frm.doc.zeitraum_von);
		}
		arbeitszeit(frm);
	}
});

function calc_monatslohn(frm) {
	if (cur_frm.doc.anstellung == 'Festanstellung') {
		var monatslohn = (cur_frm.doc.monatslohn / 100) * cur_frm.doc.anstellungsgrad;
		if (cur_frm.doc.brutto_monatslohn != monatslohn) {
			cur_frm.set_value('brutto_monatslohn', monatslohn);
		}
	}
}

function arbeitszeit(frm) {
	if (cur_frm.doc.zeitraum_bis && cur_frm.doc.zeitraum_von) {
		cur_frm.set_df_property('zeiten_summary','options', '<br><div>Bitte warten Sie bis Ihre Zeiten berechnet wurden.</div>');
		frappe.call({
			"method": "spo.utils.timesheet_handlings.calc_arbeitszeit",
			"args": {
				"employee": cur_frm.doc.name,
				"von": cur_frm.doc.zeitraum_von,
				"bis": cur_frm.doc.zeitraum_bis,
				"uebertraege": cur_frm.doc.uebertraege
			},
			"callback": function(r) {
				if (r.message != 'jahr') {
					cur_frm.set_df_property('zeiten_summary','options', '<br><div><table style="width: 100%;"><tr><th>Soll</th><th>Ist</th><th>Differenz</th></tr><tr><td>' + r.message.sollzeit + 'h</td><td>' + r.message.arbeitszeit + 'h</td><td>' + r.message.diff + 'h</td></tr></table></div>');
				} else {
					cur_frm.set_df_property('zeiten_summary','options', '<br><div>Bitte keine Jahres übergreifende abfragem durchführen!</div>');
				}
			}
		});
	} else {
		cur_frm.set_df_property('zeiten_summary','options', '<br><div>Sobald Sie ein "Von"- und ein "Bis"-Datum ausgewählt haben, erscheint hier Ihre Zeitenübersicht.</div>');
	}
}

function urlaub(frm) {
	var leave_details;
	frappe.call({
		method: "erpnext.hr.doctype.leave_application.leave_application.get_leave_details",
		async: false,
		args: {
			employee: frm.doc.name,
			date: frappe.datetime.now_date()
		},
		callback: function(r) {
			if (!r.exc && r.message['leave_allocation']) {
				leave_details = r.message['leave_allocation'];
				var leaves_taken = 0;
				if (leave_details['Persönlich'] || leave_details['Urlaub']) {
					var html = '<br><table style="width: 100%; text-align: center;"><tr><th>Urlaubsliste</th><th>Bezogen</th><th>Restsaldo</th><th>Total</th></tr>';
					if (leave_details['Urlaub']) {
					frappe.call({
							method: "spo.scripts.custom_scripts.leave_day_calculations.get_leaves_taken",
							async: false,
							args: {
								employee: frm.doc.name,
								leave_type: 'Urlaub'
							},
							callback: function(r) {
								leaves_taken = 0;
								if (r.message) {
									leaves_taken = r.message;
									html = html + '<tr style="text-align: center;"><td>Urlaub</td><td>' + leaves_taken + '</td><td>' + (leave_details["Urlaub"]["total_leaves"] - leaves_taken) + '</td><td>' + leave_details["Urlaub"]["total_leaves"] + '</td></tr>';
								}
							}
						});
					}
					if (leave_details['Persönlich']) {
						frappe.call({
							method: "spo.scripts.custom_scripts.leave_day_calculations.get_leaves_taken",
							async: false,
							args: {
								employee: frm.doc.name,
								leave_type: 'Persönlich'
							},
							callback: function(r) {
								leaves_taken = 0;
								if (r.message) {
									leaves_taken = r.message;
									html = html + '<tr style="text-align: center;"><td>Persönlich</td><td>' + leaves_taken + '</td><td>' + (leave_details["Persönlich"]["total_leaves"] - leaves_taken) + '</td><td>' + leave_details["Persönlich"]["total_leaves"] + '</td></tr>';
								}
							}
						});
					}
					html = html + '</table>';
					cur_frm.set_df_property('urlaub_overview','options', html);
				} else {
					cur_frm.set_df_property('urlaub_overview','options', '<div>Für Sie wurde noch kein Urlaub hinterlegt.</div>');
				}
			}
		}
	});
}