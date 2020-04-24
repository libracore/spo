// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mandat', {
	refresh: function(frm) {
		/* //erstellen des Dashboards, wenn ein Mitglied eingetragen ist
		if (frm.doc.mitglied) {
			update_dashboard(frm);
		} */
		//erstellen des Dashboards
		update_dashboard(frm);
		
		// timer action icon
		cur_frm.page.add_action_icon(__("fa fa-history"), function() {
			timesheet_handling(frm);
		});
		
		//update timesheet table
		frappe.call({
			"method": "spo.spo.doctype.mandat.mandat.create_zeiten_uebersicht",
			"args": {
				"dt": cur_frm.doctype,
				"name": cur_frm.doc.name
			},
			"async": false,
			"callback": function(r) {
				if (r.message) {
					cur_frm.set_df_property('zeiten_uebersicht','options', r.message);
					$("[data-funktion='open_ts']").on('click', function() {
						console.log($(this).attr("data-referenz"));
						ts_bearbeiten($(this).attr("data-referenz"));
					});
				}
			}
		});
		
		set_adress_html_felder(frm);
		
		if (cur_frm.doc.anfragen) {
			frm.add_custom_button(__("Zurück zur Anfrage"), function() {
				frappe.set_route("Form", "Anfrage", cur_frm.doc.anfragen);
			});
		}
		
		frm.add_custom_button(__("Erteilen"), function() {
			master_freigabe_erteilen(frm);
		}, __("Master Freigabe für Mandat"));
		frm.add_custom_button(__("Entfernen"), function() {
			master_freigabe_entfernen(frm);
		}, __("Master Freigabe für Mandat"));
	},
	absprung_einstellungen: function(frm) {
		frappe.set_route("Form", "Einstellungen");
	}
});


function update_dashboard(frm) {
	frappe.call({
		"method": "spo.spo.doctype.mandat.mandat.get_dashboard_data",
		"args": {
			"mitglied": frm.doc.mitglied,
			"anfrage": frm.doc.anfragen,
			"mandat": frm.doc.name
		},
		"async": false,
		"callback": function(response) {
			var query = response.message;
			var max_aufwand = query.callcenter_limit;
			if (frm.doc.max_aufwand > 0) {
				max_aufwand = frm.doc.max_aufwand;
			}
			//Limits
			var _colors = ['#d40000', '#00b000'];
			var aufwand_in_ch = query.callcenter_verwendet;
			if (aufwand_in_ch == 0) {
				_colors = ['#00b000', '#d40000'];
			} else {
				aufwand_in_ch = (aufwand_in_ch / 60) * frm.doc.stundensatz;
			}
			let limit_chart = new frappe.Chart( "#limit", { // or DOM element
				data: {
				labels: [__("Verwendet"), __("Ausstehend")],

				datasets: [
					{
						values: [aufwand_in_ch, max_aufwand - aufwand_in_ch]
					}
				],

				},
				title: __("Auswertung Kostendach (in CHF)"),
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

function timesheet_handling(frm) {
	frappe.prompt([
		{'fieldname': 'datum', 'fieldtype': 'Date', 'label': __('Datum'), 'reqd': 1, 'default': 'Today'},
		{'fieldname': 'arbeit', 'fieldtype': 'Select', 'label': __('Arbeitsinhalt'), 'reqd': 1, options: [__('Korrespondenz'), __('Telefonat'), __('Aktenstudium'), __('Organisation der juristischen Beratung'), __('Juristische Beratung'), __('Recherche Facharzt'), __('Organisation Facharzt'), __('Interne fachliche Besprechung'), __('Sonstiges')]},
		{'fieldname': 'remark', 'fieldtype': 'Small Text', 'label': __('Bemerkung'), 'reqd': 0},
		{'fieldname': 'time', 'fieldtype': 'Float', 'label': __('Arbeitszeit (in h)'), 'reqd': 1}		
	],
	function(values){
		frappe.call({
			"method": "spo.utils.timesheet_handlings.handle_timesheet",
			"args": {
				"user": frappe.session.user_email,
				"doctype": frm.doc.doctype,
				"reference": frm.doc.name,
				"time": values.time,
				"bemerkung": values.arbeit + ": " + (values.remark||''),
				"date": values.datum
			},
			"async": false,
			"callback": function(response) {
				//done
			}
		});
	},
	__('Arbeitszeit erfassen'),
	__('Erfassen')
	)
}

function ts_bearbeiten(ts) {
	frappe.call({
		"method": "spo.utils.timesheet_handlings.check_ts_owner",
		"args": {
			"ts": ts,
			"user": frappe.session.user_email
		},
		"async": false,
		"callback": function(r) {
			if (r.message) {
				frappe.route_options = {"timesheet": ts};
				frappe.set_route("Form", "Zeiterfassung");
			} else {
				frappe.msgprint(__("Sie können nur Ihre eigene Timesheets bearbeiten."), __("Nicht Ihr Timesheet"));
			}
		}
	});
}

function set_kunden_html(frm) {
	if (cur_frm.doc.customer && cur_frm.doc.kontakt && cur_frm.doc.adresse) {
		frappe.call({
			"method": "spo.spo.doctype.anfrage.anfrage.get_kunden_data",
			"args": {
				"kunde": cur_frm.doc.customer,
				"adresse": cur_frm.doc.adresse,
				"kontakt": cur_frm.doc.kontakt
			},
			"async": false,
			"callback": function(r) {
				cur_frm.set_df_property('kunde_html','options', r.message);
				cur_frm.set_df_property('kunden_dashboard_html','options', r.message);
			}
		});
	}
}

function set_angehoerige_html(frm) {
	if (cur_frm.doc.ang && cur_frm.doc.ang_adresse && cur_frm.doc.ang_kontakt) {
		frappe.call({
			"method": "spo.spo.doctype.anfrage.anfrage.get_angehoerige_data",
			"args": {
				"ang": cur_frm.doc.ang,
				"adresse": cur_frm.doc.ang_adresse,
				"kontakt": cur_frm.doc.ang_kontakt
			},
			"async": false,
			"callback": function(r) {
				cur_frm.set_df_property('ang_html','options', r.message);
			}
		});
	}
}

function set_rsv_html(frm) {
	if (cur_frm.doc.rsv && cur_frm.doc.rsv_adresse && cur_frm.doc.rsv_kontakt) {
		frappe.call({
			"method": "spo.spo.doctype.anfrage.anfrage.get_rsv_data",
			"args": {
				"rsv": cur_frm.doc.rsv,
				"adresse": cur_frm.doc.rsv_adresse,
				"kontakt": cur_frm.doc.rsv_kontakt
			},
			"async": false,
			"callback": function(r) {
				cur_frm.set_df_property('rsv_html','options', r.message);
			}
		});
	}
}


function set_adress_html_felder(frm) {
	set_kunden_html(frm);
	set_angehoerige_html(frm);
	set_rsv_html(frm);
}

function master_freigabe_erteilen(frm) {
	frappe.prompt([
		{'fieldname': 'user', 'fieldtype': 'Link', 'label': 'Benutzer', 'reqd': 1, 'options': 'User'}  
	],
	function(values){
		frappe.call({
			"method": "spo.spo.doctype.mandat.mandat.share_mandat_and_related_docs",
			"args": {
				"mandat": cur_frm.doc.name,
				"user_to_add": values.user
			},
			"async": false,
			"callback": function(r) {
				if (r.message=='ok') {
					cur_frm.reload_doc();
				}
			}
		});
	},
	'Master Freigabe erteilen',
	'Erteilen'
	);
}

function master_freigabe_entfernen(frm) {
	frappe.prompt([
		{'fieldname': 'user', 'fieldtype': 'Link', 'label': 'Benutzer', 'reqd': 1, 'options': 'User'}  
	],
	function(values){
		frappe.call({
			"method": "spo.spo.doctype.mandat.mandat.remove_share_of_mandat_and_related_docs",
			"args": {
				"mandat": cur_frm.doc.name,
				"user_to_remove": values.user
			},
			"async": false,
			"callback": function(r) {
				if (r.message=='ok') {
					cur_frm.reload_doc();
				}
			}
		});
	},
	'Master Freigabe entfernen',
	'Entfernen'
	);
}