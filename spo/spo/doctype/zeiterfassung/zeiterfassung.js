var not_block = true;
var freigabe_neukalkulation = false;
frappe.ui.form.on('Zeiterfassung', {
	refresh: function (frm) {
		clear_all(frm);
		set_ma_from_user(frm);
		set_default_start_and_end(frm);
		set_subtable_filter(frm);
		cur_frm.disable_save();
		hide_indicator(frm);
		if (frappe.user.has_role("SPO Poweruser")) {
			cur_frm.set_df_property('employee','read_only','0');
		}
	},
	employee: function (frm) {
		if (frappe.route_options.timesheet) {
			//remove_all_rows_of_all_subtables(frm);
			var ts_from_route = frappe.route_options.timesheet;
			frappe.route_options = {};
			setTimeout(function(){
				cur_frm.set_value('timesheet', ts_from_route);
			}, 1000);
		}
		set_timesheet_filter(frm);
		if (cur_frm.doc.employee) {
			frm.add_custom_button(__("Zeiterfassung speichern"), function() {
				save_update_ts(frm);
			});
		} else {
			cur_frm.remove_custom_button("Zeiterfassung speichern");
		}
		hide_indicator(frm);
	},
	datum: function (frm) {
		cur_frm.set_value('timesheet', '');
		set_timesheet_filter(frm);
	},
	timesheet: function (frm) {
		if (cur_frm.doc.timesheet) {
			remove_all_rows_of_all_subtables(frm);
			get_ts_overview(frm);
			fetch_pausen_von_ts(frm);
			fetch_beratungs_und_mandats_arbeiten_von_ts(frm);
			fetch_diverses_von_ts(frm);
		} else {
			remove_all_rows_of_all_subtables(frm);
			set_default_start_and_end(frm);
			cur_frm.set_value('arbeitszeit', 8.4);
			cur_frm.set_df_property('overview_html','options', '<div>Bitte zuerst eine(n) Mitarbeiter(in) und ein Timesheet auswählen.</div>');
			cur_frm.remove_custom_button("Zeiterfassung updaten");
			if (cur_frm.doc.employee) {
				frm.add_custom_button(__("Zeiterfassung speichern"), function() {
					save_update_ts(frm);
				});
			}
		}
	},
	start: function (frm) {
		kontrolle_input_format('start');
	},
	ende: function (frm) {
		kontrolle_input_format('ende');
	},
	arbeitszeit: function (frm) {
		neues_arbeitsende();
	},
	total_pausen: function (frm) {
		neuberechnung_arbeitszeit();
	},
	scroll_to_top1: function (frm) {
		frappe.utils.scroll_to($(".form-inner-toolbar"));
	},
	scroll_to_top2: function (frm) {
		frappe.utils.scroll_to($(".form-inner-toolbar"));
	},
	scroll_to_top3: function (frm) {
		frappe.utils.scroll_to($(".form-inner-toolbar"));
	},
	scroll_to_top4: function (frm) {
		frappe.utils.scroll_to($(".form-inner-toolbar"));
	},
	edit_submitted_ts: function (frm) {
		alles_freigeben(frm);
		frappe.msgprint("Das timesheet wurde entsperrt, Sie können nun Änderungen vornehmen.", "TS entsperrt");
		cur_frm.set_df_property('edit_submitted_ts','hidden','1');
		cur_frm.set_df_property('save_edited_ts','hidden','0');
	},
	save_edited_ts: function (frm) {
		frappe.call({
			method: "spo.spo.doctype.zeiterfassung.zeiterfassung.save_ts",
			args:{
				"ts_to_delete": cur_frm.doc.timesheet,
				"pausen": cur_frm.doc.pausen,
				"datum": cur_frm.doc.datum,
				"start": cur_frm.doc.start,
				"ende": cur_frm.doc.ende,
				"beratungen_mandate": cur_frm.doc.beratungen_mandate,
				"diverses": cur_frm.doc.diverses,
				"working_hours": cur_frm.doc.arbeitszeit,
				"ma": cur_frm.doc.employee
			},
			callback: function(r)
			{
				if (r.message) {
					cur_frm.set_value('timesheet', r.message);
					frappe.msgprint("Das Timesheet wurde erstellt.", "Erstellung erfolgreich");
					get_ts_overview(frm);
					cur_frm.set_df_property('save_edited_ts','hidden','1');
				}
			}
		});
	}
});

function kontrolle_input_format(typ) {
	var std = "08";
	var min = "00";
	var sec = "00";
	if (cur_frm.doc[typ].includes(":")) {
		if (cur_frm.doc[typ].split(":").length == 3) {
			std = parseInt(cur_frm.doc[typ].split(":")[0]);
			min = parseInt(cur_frm.doc[typ].split(":")[1]);
			sec = parseInt(cur_frm.doc[typ].split(":")[2]);
			if (std < 10) {
				std = "0" + std.toString();
			} else if (std > 23) {
				frappe.msgprint("Der Stundenwert einer Zeitangabe kann 23 nicht übersteigen.<br>Der Stundenwert '" + std.toString() + "' wurde durch '23' ersetzt.");
				std = "23";
			} else {
				std = std.toString();
			}
			if (min < 10) {
				min = "0" + min.toString();
			} else if (min > 59) {
				frappe.msgprint("Der Minutenwert einer Zeitangabe kann 59 nicht übersteigen.<br>Der Minutenwert '" + min.toString() + "' wurde durch '59' ersetzt.");
				min = "59";
			} else {
				min = min.toString();
			}
			if (sec < 10) {
				sec = "0" + sec.toString();
			} else if (sec > 59) {
				frappe.msgprint("Der Sekundenwert einer Zeitangabe kann 59 nicht übersteigen.<br>Der Sekundenwert '" + sec.toString() + "' wurde durch '59' ersetzt.");
				sec = "59";
			} else {
				sec = sec.toString();
			}
		} else if (cur_frm.doc[typ].split(":").length == 2) {
			std = parseInt(cur_frm.doc[typ].split(":")[0]);
			min = parseInt(cur_frm.doc[typ].split(":")[1]);
			sec = "00";
			if (std < 10) {
				std = "0" + std.toString();
			} else if (std > 23) {
				frappe.msgprint("Der Stundenwert einer Zeitangabe kann 23 nicht übersteigen.<br>Der Stundenwert '" + std.toString() + "' wurde durch '23' ersetzt.");
				std = "23";
			} else {
				std = std.toString();
			}
			if (min < 10) {
				min = "0" + min.toString();
			} else if (min > 59) {
				frappe.msgprint("Der Minutenwert einer Zeitangabe kann 59 nicht übersteigen.<br>Der Minutenwert '" + min.toString() + "' wurde durch '59' ersetzt.");
				min = "59";
			} else {
				min = min.toString();
			}
		} else if (cur_frm.doc[typ].split(":").length == 1) {
			std = parseInt(cur_frm.doc[typ].split(":")[0]);
			min = "00";
			sec = "00";
			if (std < 10) {
				std = "0" + std.toString();
			} else if (std > 23) {
				frappe.msgprint("Der Stundenwert einer Zeitangabe kann 23 nicht übersteigen.<br>Der Stundenwert '" + std.toString() + "' wurde durch '23' ersetzt.");
				std = "23";
			} else {
				std = std.toString();
			}
		} else {
			std = "08";
			min = "00";
			sec = "00";
			frappe.msgprint("Die Validierung der Eingabe ist fehlgeschlagen.<br>Die Eingabe wurde durch '08:00:00' ersetzt.");
		}
	} else {
		std = "08";
		min = "00";
		sec = "00";
		frappe.msgprint("Die Validierung der Eingabe ist fehlgeschlagen.<br>Die Eingabe wurde durch '08:00:00' ersetzt.");
	}
	cur_frm.set_value(typ, std + ":" + min + ":" + sec);
	if (typ == 'ende') {
		neuberechnung_arbeitszeit();
	}
	if (typ == 'start') {
		neues_arbeitsende();
	}
}

function round_3(x) {
  return Number.parseFloat(x).toFixed(3);
}

function neues_arbeitsende() {
	var total_arbeitszeit = parseFloat(cur_frm.doc.arbeitszeit + cur_frm.doc.total_pausen);
	var zu_addierende_std = parseInt(total_arbeitszeit);
	var rest_exkl_std = parseFloat(round_3(total_arbeitszeit - zu_addierende_std));
	var zu_addierende_min = parseInt(rest_exkl_std * 60);
	var rest_exkl_min = parseFloat(round_3((rest_exkl_std * 60) - zu_addierende_min));
	var zu_addierende_sec = 0;
	if (rest_exkl_min > 0) {
		zu_addierende_sec = parseInt(rest_exkl_min * 60);
	}
	var neue_std = parseInt(cur_frm.doc.start.split(":")[0]) + zu_addierende_std;
	var neue_min = parseInt(cur_frm.doc.start.split(":")[1]) + zu_addierende_min;
	var neue_sec = parseInt(cur_frm.doc.start.split(":")[2]) + zu_addierende_sec;
	while (neue_sec > 59) {
		neue_min += 1;
		neue_sec -= 59;
	}
	while (neue_min > 59) {
		neue_std += 1;
		neue_min -= 59;
	}
	var neues_ende;
	if (neue_std > 23) {
		neues_ende = '23:59:59';
		frappe.msgprint("Die eingegebene Arbeitszeit übersteigt Mitternacht! Die kann7darf nicht sein.<br>Das Arbeitsende wurde auf '23:59:59' festgesetzt.");
	}
	if (neue_std < 10) {
		neue_std = '0' + neue_std.toString();
	}
	if (neue_min < 10) {
		neue_min = '0' + neue_min.toString();
	}
	if (neue_sec < 10) {
		neue_sec = '0' + neue_sec.toString();
	}
	var neues_ende = neue_std + ":" + neue_min + ":" + neue_sec;
	cur_frm.set_value('ende', neues_ende);
}

function neuberechnung_arbeitszeit() {
	var ende_in_sec = parseFloat(cur_frm.doc.ende.split(":")[2]) + (parseFloat(cur_frm.doc.ende.split(":")[1]) * 60) + ((parseFloat(cur_frm.doc.ende.split(":")[0]) * 60) * 60);
	var start_in_sec = parseFloat(cur_frm.doc.start.split(":")[2]) + (parseFloat(cur_frm.doc.start.split(":")[1]) * 60) + ((parseFloat(cur_frm.doc.start.split(":")[0]) * 60) * 60);
	var diff_in_sec = ende_in_sec - start_in_sec;
	var diff_in_min = diff_in_sec / 60;
	var diff_in_std = diff_in_min / 60;
	cur_frm.set_value('arbeitszeit', diff_in_std - cur_frm.doc.total_pausen);
	neues_arbeitsende();
}

function clear_all(frm) {
	remove_all_rows_of_all_subtables(frm);
	cur_frm.set_value('employee', '');
	cur_frm.set_value('datum', '');
	cur_frm.set_value('timesheet', '');
	cur_frm.set_value('start', '');
	cur_frm.set_value('ende', '');
	cur_frm.set_value('arbeitszeit', '');
	cur_frm.set_value('total_pausen', 0);
	cur_frm.set_value('total_beratung', 0);
	cur_frm.set_value('total_mandatsarbeit', 0);
	cur_frm.set_value('total_diverses', 0);
}

function scroll_to_btn() {
	frappe.route_options = { 'scroll_to': { 'fieldname': 'timesheet' } };
}
frappe.ui.form.on('SPO Zeiterfassung Pause', {
	dauer: function (frm, cdt, cdn) {
		count_total_pausen(frm);
		hide_indicator(frm)
	},
	pausen_remove: function (frm) {
		count_total_pausen(frm);
		hide_indicator(frm)
	}
});

frappe.ui.form.on('SPO Zeiterfassung Beratung Mandate', {
	dauer: function (frm, cdt, cdn) {
		count_total_beratungen_mandate(frm);
		hide_indicator(frm)
	},
	beratungen_mandate_remove: function (frm) {
		count_total_beratungen_mandate(frm);
		hide_indicator(frm)
	}
});

frappe.ui.form.on('SPO Zeiterfassung Diverses', {
	dauer: function (frm, cdt, cdn) {
		count_total_diverses(frm);
		hide_indicator(frm)
	},
	diverses_remove: function (frm) {
		count_total_diverses(frm);
		hide_indicator(frm)
	}
});

function hide_indicator(frm) {
	var indicator = $(".indicator");
	indicator.hide();
}

function set_ma_from_user(frm) {
	var user = frappe.session.user_email;
	frappe.call({
		method: "spo.spo.doctype.zeiterfassung.zeiterfassung.get_ma_from_user",
		args:{
			"user": user
		},
		callback: function(r)
		{
			if (r.message) {
				cur_frm.set_value('employee', r.message);
				if (r.message != '') {
					cur_frm.scroll_to_field("timesheet");
				} else {
					cur_frm.scroll_to_field("employee");
				}
			}
		}
	});
}

function remove_all_rows_of_all_subtables(frm) {
	alles_freigeben(frm);
	//pausen
	var tbl = frm.doc.pausen || [];
	var i = tbl.length;
	while (i--)
	{
		cur_frm.get_field("pausen").grid.grid_rows[i].remove();
	}
	cur_frm.refresh_field('pausen');
	
	//beratungen_mandate
	tbl = frm.doc.beratungen_mandate || [];
	var i = tbl.length;
	while (i--)
	{
		cur_frm.get_field("beratungen_mandate").grid.grid_rows[i].remove();
	}
	cur_frm.refresh_field('beratungen_mandate');
	
	//diverses
	tbl = frm.doc.diverses || [];
	var i = tbl.length;
	while (i--)
	{
		cur_frm.get_field("diverses").grid.grid_rows[i].remove();
	}
	cur_frm.refresh_field('diverses');
}

function set_subtable_filter(frm) {
	frm.set_query('spo_dokument', 'beratungen_mandate', function () {
		return {
			'filters': {
				'module': 'SPO',
				'istable': 0,
				'name': ['not in', ['Zeiterfassung', 'Mitgliedschaft', 'Einstellungen', 'SPO textbausteine']]
			}
		};
	});
	frm.set_query('activity_type', 'diverses', function () {
		return {
			'filters': {
				'name': ['not in', ['Beratung', 'Mandatsarbeit', 'Pause', 'Arbeitszeit']]
			}
		};
	});
}

function count_total_pausen(frm) {
	cur_frm.set_value('total_pausen', 0);
	var i;
	for (i=0; i < cur_frm.doc.pausen.length; i++) {
		cur_frm.set_value('total_pausen', cur_frm.doc.total_pausen + cur_frm.doc.pausen[i].dauer);
		cur_frm.refresh_field("total_pausen");
	}
	setTimeout(function(){ cur_frm.refresh_field("total_pausen"); }, 1000);
}

function set_timesheet_filter(frm) {
	cur_frm.fields_dict['timesheet'].get_query = function(doc) {
		return {
			filters: {
				"employee": cur_frm.doc.employee,
				"start_date": cur_frm.doc.datum,
				"docstatus": ['!=', 2]
			}
		}
	}
}

function get_ts_overview(frm) {
	frappe.call({
		method: "spo.spo.doctype.zeiterfassung.zeiterfassung.get_visual_overview",
		args:{
			"ts": cur_frm.doc.timesheet
		},
		callback: function(r)
		{
			if (r.message) {
				cur_frm.set_df_property('overview_html','options', r.message.html);
				var diff_zu_arbeitszeit = r.message.arbeitszeit - (r.message.total_beratungszeit + r.message.total_mandatszeit + r.message.total_diverses);
				if (diff_zu_arbeitszeit < 0) {
					diff_zu_arbeitszeit = (r.message.total_beratungszeit + r.message.total_mandatszeit + r.message.total_diverses) - r.message.arbeitszeit;
				} else {
					cur_frm.set_value('total_differenz', diff_zu_arbeitszeit);
				}
				const data = {
					labels: ["Arbeitszeit", "Beratung", "Mandatsarbeit", "Diverses", "Differenz"],
					datasets: [
						{ values: [r.message.arbeitszeit, r.message.total_beratungszeit, r.message.total_mandatszeit, r.message.total_diverses, diff_zu_arbeitszeit] }
					]
				}
				new frappe.Chart( "#chart", {
					data: data,
					type: 'pie',
					height: 350,
					colors: ['green']
				});
				if (r.message.docstatus == 1) {
					frappe.msgprint("Dieses Timesheet wurde bereits verbucht und kann nur noch betrachtet werden.", "Timesheet bereits verbucht");
					cur_frm.remove_custom_button("Zeiterfassung speichern");
					alles_sperren(frm);
					if (frappe.user.has_role("SPO Poweruser")) {
						cur_frm.set_df_property('edit_submitted_ts','hidden','0');
					}
				} else {
					cur_frm.remove_custom_button("Zeiterfassung speichern");
					frm.add_custom_button(__("Zeiterfassung updaten"), function() {
						save_update_ts(frm);
					});
				}
			}
		}
	});
}

function save_update_ts(frm) {
	var overlapp = check_overlapp(frm);
	if (!overlapp) {
		if(cur_frm.doc.timesheet) {
			frappe.call({
				method: "spo.spo.doctype.zeiterfassung.zeiterfassung.update_ts",
				args:{
					"ma": cur_frm.doc.employee,
					"ts": cur_frm.doc.timesheet,
					"pausen": cur_frm.doc.pausen,
					"datum": cur_frm.doc.datum,
					"start": cur_frm.doc.start,
					"ende": cur_frm.doc.ende,
					"beratungen_mandate": cur_frm.doc.beratungen_mandate,
					"diverses": cur_frm.doc.diverses,
					"working_hours": cur_frm.doc.arbeitszeit
				},
				callback: function(r)
				{
					if (r.message == 'ok') {
						frappe.msgprint("Das Timesheet wurde angepasst.", "Update erfolgreich");
						get_ts_overview(frm);
					}
				}
			});
		} else {
			frappe.call({
				method: "spo.spo.doctype.zeiterfassung.zeiterfassung.save_ts",
				args:{
					"ts_to_delete": '',
					"pausen": cur_frm.doc.pausen,
					"datum": cur_frm.doc.datum,
					"start": cur_frm.doc.start,
					"ende": cur_frm.doc.ende,
					"beratungen_mandate": cur_frm.doc.beratungen_mandate,
					"diverses": cur_frm.doc.diverses,
					"working_hours": cur_frm.doc.arbeitszeit,
					"ma": cur_frm.doc.employee
				},
				callback: function(r)
				{
					if (r.message) {
						cur_frm.set_value('timesheet', r.message);
						frappe.msgprint("Das Timesheet wurde erstellt.", "Erstellung erfolgreich");
						get_ts_overview(frm);
					}
				}
			});
		}
	}
}

function check_overlapp(frm) {
	var total_time = cur_frm.doc.arbeitszeit - cur_frm.doc.total_beratung - cur_frm.doc.total_mandatsarbeit - cur_frm.doc.total_diverses;
	if (total_time < 0) {
		frappe.msgprint("Die Summe von Beratungen, Mandatsarbeiten und diversen Arbeiten übersteigt Ihre Arbeitszeit.", "Arbeitszeit zu kurz");
		return true
	} else {
		return false
	}
}

function alles_sperren(frm) {
	cur_frm.set_df_property('start','read_only','1');
	cur_frm.set_df_property('ende','read_only','1');
	cur_frm.set_df_property('arbeitszeit','read_only','1');
	cur_frm.set_df_property('pausen','read_only','1');
	cur_frm.set_df_property('total_pausen','read_only','1');
	cur_frm.set_df_property('beratungen_mandate','read_only','1');
	cur_frm.set_df_property('total_beratung','read_only','1');
	cur_frm.set_df_property('total_mandatsarbeit','read_only','1');
	cur_frm.set_df_property('diverses','read_only','1');
	cur_frm.set_df_property('total_diverses','read_only','1');
	var pause_from = frappe.meta.get_docfield("SPO Zeiterfassung Pause","from", cur_frm.doc.name);
	var pause_dauer = frappe.meta.get_docfield("SPO Zeiterfassung Pause","dauer", cur_frm.doc.name);
	pause_from.read_only = 1;
	pause_dauer.read_only = 1;
	var beratung_referenz = frappe.meta.get_docfield("SPO Zeiterfassung Beratung Mandate","spo_referenz", cur_frm.doc.name);
	var beratung_dauer = frappe.meta.get_docfield("SPO Zeiterfassung Beratung Mandate","dauer", cur_frm.doc.name);
	var beratung_dokument = frappe.meta.get_docfield("SPO Zeiterfassung Beratung Mandate","spo_dokument", cur_frm.doc.name);
	beratung_referenz.read_only = 1;
	beratung_dauer.read_only = 1;
	beratung_dokument.read_only = 1;
	var diverses_activity_type = frappe.meta.get_docfield("SPO Zeiterfassung Diverses","activity_type", cur_frm.doc.name);
	var diverses_dauer = frappe.meta.get_docfield("SPO Zeiterfassung Diverses","dauer", cur_frm.doc.name);
	diverses_activity_type.read_only = 1;
	diverses_dauer.read_only = 1;
	cur_frm.remove_custom_button("Zeiterfassung updaten");
}

function alles_freigeben(frm) {
	cur_frm.set_df_property('start','read_only','0');
	cur_frm.set_df_property('ende','read_only','0');
	cur_frm.set_df_property('arbeitszeit','read_only','0');
	cur_frm.set_df_property('pausen','read_only','0');
	cur_frm.set_df_property('beratungen_mandate','read_only','0');
	cur_frm.set_df_property('diverses','read_only','0');
	var pause_from = frappe.meta.get_docfield("SPO Zeiterfassung Pause","from", cur_frm.doc.name);
	var pause_dauer = frappe.meta.get_docfield("SPO Zeiterfassung Pause","dauer", cur_frm.doc.name);
	pause_from.read_only = 0;
	pause_dauer.read_only = 0;
	var beratung_referenz = frappe.meta.get_docfield("SPO Zeiterfassung Beratung Mandate","spo_referenz", cur_frm.doc.name);
	var beratung_dauer = frappe.meta.get_docfield("SPO Zeiterfassung Beratung Mandate","dauer", cur_frm.doc.name);
	var beratung_dokument = frappe.meta.get_docfield("SPO Zeiterfassung Beratung Mandate","spo_dokument", cur_frm.doc.name);
	beratung_referenz.read_only = 0;
	beratung_dauer.read_only = 0;
	beratung_dokument.read_only = 0;
	var diverses_activity_type = frappe.meta.get_docfield("SPO Zeiterfassung Diverses","activity_type", cur_frm.doc.name);
	var diverses_dauer = frappe.meta.get_docfield("SPO Zeiterfassung Diverses","dauer", cur_frm.doc.name);
	diverses_activity_type.read_only = 0;
	diverses_dauer.read_only = 0;
}

function set_default_start_and_end(frm) {
	var heute = frappe.datetime.now_date();
	cur_frm.set_value('start', '08:00:00');
	cur_frm.set_value('ende', '17:54:00');
	cur_frm.set_value('datum', heute);
	
	var child = cur_frm.add_child('pausen');
	frappe.model.set_value(child.doctype, child.name, 'from', "12:00:00");
	frappe.model.set_value(child.doctype, child.name, 'dauer', 1.5);
	cur_frm.refresh_field('pausen');
}

function fetch_pausen_von_ts(frm) {
	frappe.call({
		method: "spo.spo.doctype.zeiterfassung.zeiterfassung.fetch_pausen_von_ts",
		args:{
			"ts": cur_frm.doc.timesheet
		},
		callback: function(r)
		{
			if (r.message) {
				fetch = r.message;
				cur_frm.set_value('start', fetch.start);
				cur_frm.set_value('ende', fetch.ende);
				cur_frm.set_value('arbeitszeit', fetch.total_arbeitszeit);
				cur_frm.set_value('total_pausen', fetch.total_pausenzeit);
				var i;
				for (i=0; i < fetch.pausen.length; i++) {
					var child = cur_frm.add_child('pausen');
					frappe.model.set_value(child.doctype, child.name, 'from', fetch.pausen[i].start);
					frappe.model.set_value(child.doctype, child.name, 'dauer', fetch.pausen[i].dauer);
					frappe.model.set_value(child.doctype, child.name, 'referenz', fetch.pausen[i].referenz);
				}
				cur_frm.refresh_field('pausen');
			}
		}
	});
}

function fetch_beratungs_und_mandats_arbeiten_von_ts(frm) {
	frappe.call({
		method: "spo.spo.doctype.zeiterfassung.zeiterfassung.fetch_beratungs_und_mandats_arbeiten_von_ts",
		args:{
			"ts": cur_frm.doc.timesheet
		},
		callback: function(r)
		{
			if (r.message) {
				fetch = r.message;
				cur_frm.set_value('total_beratung', fetch.total_beratung);
				cur_frm.set_value('total_mandatsarbeit', fetch.total_mandatsarbeit);
				var i;
				for (i=0; i < fetch.beratungen.length; i++) {
					var child = cur_frm.add_child('beratungen_mandate');
					frappe.model.set_value(child.doctype, child.name, 'spo_referenz', fetch.beratungen[i].spo_referenz);
					frappe.model.set_value(child.doctype, child.name, 'arbeit', fetch.beratungen[i].arbeit);
					frappe.model.set_value(child.doctype, child.name, 'dauer', fetch.beratungen[i].dauer);
					frappe.model.set_value(child.doctype, child.name, 'referenz', fetch.beratungen[i].referenz);
					frappe.model.set_value(child.doctype, child.name, 'spo_dokument', fetch.beratungen[i].spo_dokument);
					frappe.model.set_value(child.doctype, child.name, 'beratung', fetch.beratungen[i].beratung);
					frappe.model.set_value(child.doctype, child.name, 'mandat', fetch.beratungen[i].mandat);
				}
				cur_frm.refresh_field('beratungen_mandate');
			}
		}
	});
}

function count_total_beratungen_mandate(frm) {
	cur_frm.set_value('total_beratung', 0);
	cur_frm.set_value('total_mandatsarbeit', 0);
	var i;
	for (i=0; i < cur_frm.doc.beratungen_mandate.length; i++) {
		if (cur_frm.doc.beratungen_mandate[i].beratung == 1) {
			cur_frm.set_value('total_beratung', cur_frm.doc.total_beratung + cur_frm.doc.beratungen_mandate[i].dauer);
			cur_frm.refresh_field("total_beratung");
		}
		if (cur_frm.doc.beratungen_mandate[i].mandat == 1) {
			cur_frm.set_value('total_mandatsarbeit', cur_frm.doc.total_mandatsarbeit + cur_frm.doc.beratungen_mandate[i].dauer);
			cur_frm.refresh_field("total_mandatsarbeit");
		}
	}
	setTimeout(function(){
		cur_frm.refresh_field("total_beratung");
		cur_frm.refresh_field("total_mandatsarbeit");
	}, 1000);
}

function fetch_diverses_von_ts(frm) {
	frappe.call({
		method: "spo.spo.doctype.zeiterfassung.zeiterfassung.fetch_diverses_von_ts",
		args:{
			"ts": cur_frm.doc.timesheet
		},
		callback: function(r)
		{
			if (r.message) {
				fetch = r.message;
				cur_frm.set_value('total_diverses', fetch.total_diverses);
				var i;
				for (i=0; i < fetch.diverses.length; i++) {
					var child = cur_frm.add_child('diverses');
					frappe.model.set_value(child.doctype, child.name, 'activity_type', fetch.diverses[i].activity_type);
					frappe.model.set_value(child.doctype, child.name, 'dauer', fetch.diverses[i].dauer);
					frappe.model.set_value(child.doctype, child.name, 'referenz', fetch.diverses[i].referenz);
				}
				cur_frm.refresh_field('diverses');
			}
		}
	});
}

function count_total_diverses(frm) {
	cur_frm.set_value('total_diverses', 0);
	var i;
	for (i=0; i < cur_frm.doc.diverses.length; i++) {
		cur_frm.set_value('total_diverses', cur_frm.doc.total_diverses + cur_frm.doc.diverses[i].dauer);
		cur_frm.refresh_field("total_diverses");
	}
	setTimeout(function(){ cur_frm.refresh_field("total_diverses"); }, 1000);
}