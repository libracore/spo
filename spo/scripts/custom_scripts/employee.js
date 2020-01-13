frappe.ui.form.on('Employee', {
	validate: function(frm) {
		calc_monatslohn(frm);	
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
		frappe.call({
			"method": "spo.utils.timesheet_handlings.calc_arbeitszeit",
			"args": {
				"employee": cur_frm.doc.name,
				"von": cur_frm.doc.zeitraum_von,
				"bis": cur_frm.doc.zeitraum_bis
			},
			"callback": function(r) {
				if (r.message) {
					cur_frm.set_df_property('zeiten_summary','options', '<div>Sie haben im gewählten Zeitraum <b>' + r.message + 'h</b> gearbeitet.<br>Für detailierte Tagesinformationen öffnen Sie bitte Ihr entsprechendes Timesheet im Zeiterfassungs Manager.</div>');
				}
			}
		});
	}
}