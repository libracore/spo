var not_block = true;
frappe.ui.form.on('Zeiterfassung', {
	onload: function (frm) {
		/* console.log("jez");
		set_ma_from_user(frm);
		set_default_start_and_end(frm);
		set_subtable_filter(frm); */
	},
	refresh: function (frm) {
		clear_all(frm);
		set_ma_from_user(frm);
		set_default_start_and_end(frm);
		set_subtable_filter(frm);
		cur_frm.disable_save();
		hide_indicator(frm);
		//console.log("refresh");
	},
	employee: function (frm) {
		//console.log("employee");
		if (frappe.route_options.timesheet) {
			//remove_all_rows_of_all_subtables(frm);
			var ts_from_route = frappe.route_options.timesheet;
			frappe.route_options = {};
			setTimeout(function(){
				cur_frm.set_value('timesheet', ts_from_route);
				//frappe.route_options = {};
				//console.log("fetch ts");
			}, 1000);
			/* cur_frm.set_value('timesheet', frappe.route_options.timesheet);
			frappe.route_options = {}; */
		}/*  else {
			cur_frm.set_value('timesheet', '');
		} */
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
		if (cur_frm.doc.start.includes(":")) {
			if (cur_frm.doc.start.split(":").length == 3) {
					recalc_end_time(frm);
			} else {
				var start = cur_frm.doc.start.replace(":", "");
				if (start.length == 6) {
					cur_frm.set_value('start', start.split("")[0] + start.split("")[1] + ":" + start.split("")[2] + start.split("")[3] + ":" + start.split("")[4] + start.split("")[5]);
				} else if (start.length == 4) {
					cur_frm.set_value('start', start.split("")[0] + start.split("")[1] + ":" + start.split("")[2] + start.split("")[3] + ":00");
				} else if (start.length == 4) {
					cur_frm.set_value('start', start.split("")[0] + start.split("")[1] + ":" + start.split("")[2] + start.split("")[3] + ":00");
				} else if (start.length == 2) {
					cur_frm.set_value('start', start.split("")[0] + start.split("")[1] + ":00:00");
				} else if (start.length == 1) {
					cur_frm.set_value('start', "0" + start + ":00:00");
				}
			}
		} else {
			var start = cur_frm.doc.start.replace(":", "");
			if (start.length == 6) {
				cur_frm.set_value('start', start.split("")[0] + start.split("")[1] + ":" + start.split("")[2] + start.split("")[3] + ":" + start.split("")[4] + start.split("")[5]);
			} else if (start.length == 4) {
				cur_frm.set_value('start', start.split("")[0] + start.split("")[1] + ":" + start.split("")[2] + start.split("")[3] + ":00");
			} else if (start.length == 4) {
				cur_frm.set_value('start', start.split("")[0] + start.split("")[1] + ":" + start.split("")[2] + start.split("")[3] + ":00");
			} else if (start.length == 2) {
				cur_frm.set_value('start', start.split("")[0] + start.split("")[1] + ":00:00");
			} else if (start.length == 1) {
				cur_frm.set_value('start', "0" + start + ":00:00");
			}
		}
	},
	ende: function (frm) {
		if (cur_frm.doc.ende.includes(":")) {
			if (cur_frm.doc.ende.split(":").length == 3) {
					if (not_block) {
						calc_arbeitszeit(cur_frm.doc.start, cur_frm.doc.ende, frm);
					} else {
						not_block = true;
					}
			} else {
				var ende = cur_frm.doc.ende.replace(":", "");
				if (ende.length == 6) {
					cur_frm.set_value('ende', ende.split("")[0] + ende.split("")[1] + ":" + ende.split("")[2] + ende.split("")[3] + ":" + ende.split("")[4] + ende.split("")[5]);
				} else if (ende.length == 4) {
					cur_frm.set_value('ende', ende.split("")[0] + ende.split("")[1] + ":" + ende.split("")[2] + ende.split("")[3] + ":00");
				} else if (ende.length == 2) {
					cur_frm.set_value('ende', ende.split("")[0] + ende.split("")[1] + ":00:00");
				} else if (ende.length == 1) {
					cur_frm.set_value('ende', "0" + ende + ":00:00");
				}
			}
		} else {
			var ende = cur_frm.doc.ende.replace(":", "");
			if (ende.length == 6) {
				cur_frm.set_value('ende', ende.split("")[0] + ende.split("")[1] + ":" + ende.split("")[2] + ende.split("")[3] + ":" + ende.split("")[4] + ende.split("")[5]);
			} else if (ende.length == 4) {
				cur_frm.set_value('ende', ende.split("")[0] + ende.split("")[1] + ":" + ende.split("")[2] + ende.split("")[3] + ":00");
			} else if (ende.length == 2) {
				cur_frm.set_value('ende', ende.split("")[0] + ende.split("")[1] + ":00:00");
			} else if (ende.length == 1) {
				cur_frm.set_value('ende', "0" + ende + ":00:00");
			}
		}
	},
	arbeitszeit: function (frm) {
		recalc_end_time(frm);
	},
	total_pausen: function (frm) {
		recalc_end_time(frm);
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
	}
});

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
					"ts": cur_frm.doc.timesheet,
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
	//console.log("default calc");
	var start_zeit = frappe.datetime.now_time();
	var end_zeit = calc_end_time(start_zeit, 0);
	var heute = frappe.datetime.now_date();
	cur_frm.set_value('start', start_zeit);
	cur_frm.set_value('ende', end_zeit);
	cur_frm.set_value('datum', heute);
}

function recalc_end_time(frm) {
	//console.log("recalc");
	if (cur_frm.doc.start) {
		var start = cur_frm.doc.start;
		var diff = 0;
		if (Number(parseFloat(cur_frm.doc.arbeitszeit).toFixed(3)) != 8.4) {	
			var diff = Number(parseFloat(cur_frm.doc.arbeitszeit).toFixed(3)) - 8.4;
		}
		var ende = calc_end_time(start, diff + cur_frm.doc.total_pausen);
		not_block = false;
		cur_frm.set_value('ende', ende);
	}
}

function calc_end_time(start_zeit, pausen_dauer) {
	pausen_dauer = 60 * Number(parseFloat(pausen_dauer).toFixed(1));
	var stunden = parseInt(start_zeit.split(":")[0]);
	var end_stunden = stunden + 8;
	var minuten = (parseInt(start_zeit.split(":")[1]) + 24) + pausen_dauer;
	while (minuten < 0) {
		end_stunden = end_stunden - 1;
		minuten = minuten + 60;
	}
	
	while (minuten >= 60) {
		end_stunden = end_stunden + 1;
		minuten = minuten - 60;
	}
	var end_minuten = parseInt(minuten);
	if (end_minuten < 10) {
		end_minuten = '0' + end_minuten.toString();
	}
	var end_zeit = end_stunden.toString() + ":" + end_minuten.toString() + ":" + start_zeit.split(":")[2].toString();
	if (end_stunden > 23) {
		end_zeit = "23:59:59";
	}
	
	return end_zeit;
}

function calc_arbeitszeit(start, end, frm) {
	start = start.split(":");
    end = end.split(":");
    var startDate = new Date(0, 0, 0, start[0], start[1], 0);
    var endDate = new Date(0, 0, 0, end[0], end[1], 0);
    var diff = endDate.getTime() - startDate.getTime();
	var hours = Math.floor(diff / 1000 / 60 / 60);
	diff -= hours * 1000 * 60 * 60;
    var minutes = Math.floor(diff / 1000 / 60);

    if (hours < 0)
       hours = hours + 24;
   
    minutes = minutes / 60;
	
	cur_frm.set_value('arbeitszeit', hours + "." + minutes.toString().split(".")[1]);
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