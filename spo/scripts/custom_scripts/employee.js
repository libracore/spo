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
		cur_frm.set_df_property('zeiten_summary','options', '<div>Bitte warten Sie bis Ihre Zeiten berechnet wurden.</div>');
		frappe.call({
			"method": "spo.utils.timesheet_handlings.calc_arbeitszeit",
			"args": {
				"employee": cur_frm.doc.name,
				"von": cur_frm.doc.zeitraum_von,
				"bis": cur_frm.doc.zeitraum_bis
			},
			"callback": function(r) {
				if (r.message) {
					//cur_frm.set_df_property('zeiten_summary','options', '<div><br><br><b>Soll:</b> ' + r.message.sollzeit + 'h<br><b>Ist:</b> ' + r.message.arbeitszeit + 'h<br><b>Differenz:</b> ' + r.message.diff + 'h</div>');
					cur_frm.set_df_property('zeiten_summary','options', '<div><table style="width: 100%;"><tr><th>Soll</th><th>Ist</th><th>Differenz</th></tr><tr><td>' + r.message.sollzeit + 'h</td><td>' + r.message.arbeitszeit + 'h</td><td>' + r.message.diff + 'h</td></tr></table></div>');
				}
			}
		});
	} else {
		cur_frm.set_df_property('zeiten_summary','options', '<div>Sobald Sie ein "Von"- und ein "Bis"-Datum ausgewählt haben, erscheint hier Ihre Zeitenübersicht.</div>');
	}
}