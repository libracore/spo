/* frappe.ui.form.on('Zeiterfassung', {
	employee: function (frm) {
		set_timesheet_filter(frm);
	},
	datum: function (frm) {
		set_timesheet_filter(frm);
	},
	timesheet: function (frm) {
		get_ts_overview(frm);
	},
	onload: function (frm) {
		set_default_start_and_end(frm);
	},
	start: function (frm) {
		if (cur_frm.doc.start.includes(":")) {
			if (cur_frm.doc.start.split(":").length == 3) {
					recalc_end_time(frm);
			} else {
				var start = cur_frm.doc.start.replace(":", "");
				if (start.length == 6) {
					cur_frm.set_value('start', start.split("")[0] + start.split("")[1] + ":" + start.split("")[2] + start.split("")[3] + ":" + start.split("")[4] + start.split("")[5]);
				}
			}
		} else {
			var start = cur_frm.doc.start.replace(":", "");
			if (start.length == 6) {
				cur_frm.set_value('start', start.split("")[0] + start.split("")[1] + ":" + start.split("")[2] + start.split("")[3] + ":" + start.split("")[4] + start.split("")[5]);
			} else if (start.length == 4) {
				cur_frm.set_value('start', start.split("")[0] + start.split("")[1] + ":" + start.split("")[2] + start.split("")[3] + ":00");
			}
		}
	},
	ende: function (frm) {
		if (cur_frm.doc.ende.includes(":")) {
			if (cur_frm.doc.ende.split(":").length == 3) {
					calc_arbeitszeit(cur_frm.doc.start, cur_frm.doc.ende, frm);
			} else {
				var ende = cur_frm.doc.ende.replace(":", "");
				if (ende.length == 6) {
					cur_frm.set_value('ende', ende.split("")[0] + ende.split("")[1] + ":" + ende.split("")[2] + ende.split("")[3] + ":" + ende.split("")[4] + ende.split("")[5]);
				}
			}
		} else {
			var ende = cur_frm.doc.ende.replace(":", "");
			if (ende.length == 6) {
				cur_frm.set_value('ende', ende.split("")[0] + ende.split("")[1] + ":" + ende.split("")[2] + ende.split("")[3] + ":" + ende.split("")[4] + ende.split("")[5]);
			} else if (ende.length == 4) {
				cur_frm.set_value('ende', ende.split("")[0] + ende.split("")[1] + ":" + ende.split("")[2] + ende.split("")[3] + ":00");
			}
		}
	}
})

function set_timesheet_filter(frm) {
	cur_frm.fields_dict['timesheet'].get_query = function(doc) {
		return {
			filters: {
				"employee": frm.doc.employee,
				"start_date": frm.doc.datum
			}
		}
	}
}

function get_ts_overview(frm) {
	frappe.call({
		method: "spo.utils.timesheet_handlings.get_visual_overview",
		args:{
			"ts": frm.doc.timesheet
		},
		callback: function(r)
		{
			if (r.message) {
				cur_frm.set_df_property('overview_html','options', r.message);
			}
		}
	});
}

function set_default_start_and_end(frm) {
	var start_zeit = frappe.datetime.now_time();
	var end_zeit = calc_end_time(start_zeit, 0);
	cur_frm.set_value('ende', end_zeit);
}

function recalc_end_time(frm) {
	var start_zeit = cur_frm.doc.start;
	var end_zeit = calc_end_time(start_zeit, 0);
	cur_frm.set_value('ende', end_zeit);
}

function calc_end_time(start_zeit, pausen_dauer) {
	pausen_dauer = 60 * parseFloat(pausen_dauer);
	var stunden = parseInt(start_zeit.split(":")[0]);
	var end_stunden = stunden + 8;
	var minuten = (parseInt(start_zeit.split(":")[1]) + 24) + pausen_dauer;
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
} */