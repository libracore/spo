// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vollmacht', {
	onload: function(frm) {
		check_todesfall(frm);
		set_kunden_html(frm);
		set_ang_html(frm)
		if (cur_frm.doc.todesfall == 1) {
			fetch_data_from_ang(frm);
		} else {
			fetch_data_from_kunde(frm);
		}
	},
	before_save: function(frm) {
		if (!cur_frm.doc.titelzeile && !cur_frm.doc.todesfall) {
			var titelzeile_string = '<p><b>Abklärungen im Zusammenhang mit</b> (dem Eingriffes/ der Operation) <b>vom</b> (Datum)  <b>im Spital XY</b> (Ort) <b>samt</b> (Folgen) oder (inkl. Vor- und Nachbehandlung)<b>.</b></p>';
			cur_frm.set_value('titelzeile', titelzeile_string);
		} else if (!cur_frm.doc.titelzeile && cur_frm.doc.todesfall) {
			var titelzeile_string = '<p><b>Abklärung der medizinischen Behandlung vom</b> (Datum) <b>im Spital XY</b> (Ort) <b>samt Folgen im Zusammenhang mit dem Todesfall betreffend Herrn/Frau/des Kindes</b> (fett: † Name, geb*   – gest., Adresse) <b>insbesondere vollständige Einsicht in die damit verbundenen Akten.</b></p>';
			cur_frm.set_value('titelzeile', titelzeile_string);
		}
	},
	refresh: function(frm) {
		// timer action icon
		cur_frm.page.add_action_icon(__("fa fa-history"), function() {
			timesheet_handling(frm);
		});
		
		
		if (!cur_frm.doc.berater) {
			cur_frm.set_value('berater', frappe.user_info().fullname);
		}
		
		// filter for textbaustein (titelzeile) based on doctype and user
		cur_frm.fields_dict['textkonserve'].get_query = function(doc) {
			 return {
				 filters: {
					 "mitarbeiter": frappe.user.name,
					 "dokument": "Vollmacht - Titelzeile"
				 }
			 }
		}
		
		// filter for textbaustein (begleitbrief) based on doctype and user
		cur_frm.fields_dict['textkonserve_begleitbrief'].get_query = function(doc) {
			 return {
				 filters: {
					 "mitarbeiter": frappe.user.name,
					 "dokument": "Vollmacht - Begleitbrief"
				 }
			 }
		}
		
		check_todesfall(frm);
		set_kunden_html(frm);
		set_ang_html(frm);
		
		if (cur_frm.doc.mandat) {
			frm.add_custom_button(__("Zurück zum Mandat"), function() {
				frappe.set_route("Form", "Mandat", cur_frm.doc.mandat);
			});
		}
	},
	todesfall: function(frm) {
		if (cur_frm.doc.todesfall == 1) {
			fetch_data_from_ang(frm);
		} else {
			fetch_data_from_kunde(frm);
		}
	}
});

function fetch_data_from_ang(frm) {
	if (cur_frm.doc.ang_kontakt && cur_frm.doc.ang_adresse) {
		frappe.call({
			"method": "spo.spo.doctype.vollmacht.vollmacht.get_fetching_data",
			"args": {
				"adresse": cur_frm.doc.ang_adresse,
				"kontakt": cur_frm.doc.ang_kontakt
			},
			"async": false,
			"callback": function(r) {
				if (r) {
					var adresse = r.message.adresse;
					var kontakt = r.message.kontakt;
					
					cur_frm.set_value("name_vorname", kontakt.first_name + " " + kontakt.last_name);
					cur_frm.set_value("geburtsdatum", kontakt.geburtsdatum);
					cur_frm.set_value("adresse", adresse.address_line1);
					cur_frm.set_value("email", kontakt.email_id);
					if (kontakt.phone) {
						cur_frm.set_value("telefon", kontakt.phone);
					} else if (kontakt.mobile_no) {
						cur_frm.set_value("telefon", kontakt.mobile_no);
					}
				}
			}
		});
	}
}

function fetch_data_from_kunde(frm) {
	if (cur_frm.doc.kunden_kontakt && cur_frm.doc.kunden_adresse) {
		frappe.call({
			"method": "spo.spo.doctype.vollmacht.vollmacht.get_fetching_data",
			"args": {
				"adresse": cur_frm.doc.kunden_adresse,
				"kontakt": cur_frm.doc.kunden_kontakt
			},
			"async": false,
			"callback": function(r) {
				if (r) {
					var adresse = r.message.adresse;
					var kontakt = r.message.kontakt;
					
					cur_frm.set_value("name_vorname", kontakt.first_name + " " + kontakt.last_name);
					cur_frm.set_value("geburtsdatum", kontakt.geburtsdatum);
					cur_frm.set_value("adresse", adresse.address_line1);
					cur_frm.set_value("email", kontakt.email_id);
					if (kontakt.phone) {
						cur_frm.set_value("telefon", kontakt.phone);
					} else if (kontakt.mobile_no) {
						cur_frm.set_value("telefon", kontakt.mobile_no);
					}
				}
			}
		});
	}
}

function check_todesfall(frm) {
	if (cur_frm.doc.mandat) {
		frappe.call({
			"method": "spo.spo.doctype.vollmacht.vollmacht.check_todesfall",
			"args": {
				"mandat": cur_frm.doc.mandat
			},
			"async": false,
			"callback": function(r) {
				cur_frm.set_value("todesfall", r.message);
			}
		});
	}
}

function set_kunden_html(frm) {
	if (cur_frm.doc.customer && cur_frm.doc.kunden_kontakt && cur_frm.doc.kunden_adresse) {
		frappe.call({
			"method": "spo.spo.doctype.vollmacht.vollmacht.get_kunden_data",
			"args": {
				"kunde": cur_frm.doc.customer,
				"adresse": cur_frm.doc.kunden_adresse,
				"kontakt": cur_frm.doc.kunden_kontakt
			},
			"async": false,
			"callback": function(r) {
				cur_frm.set_df_property('kunde_html','options', r.message);
			}
		});
	}
}

function set_ang_html(frm) {
	if (cur_frm.doc.ang && cur_frm.doc.ang_kontakt && cur_frm.doc.ang_adresse) {
		frappe.call({
			"method": "spo.spo.doctype.vollmacht.vollmacht.get_ang_data",
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

function timesheet_handling(frm) {
	frappe.prompt([
		{'fieldname': 'datum', 'fieldtype': 'Date', 'label': 'Datum', 'reqd': 1, 'default': 'Today'},
		{'fieldname': 'time', 'fieldtype': 'Float', 'label': 'Arbeitszeit (in h)', 'reqd': 1}  
	],
	function(values){
		frappe.call({
			"method": "spo.utils.timesheet_handlings.handle_timesheet",
			"args": {
				"user": frappe.session.user_email,
				"doctype": frm.doc.doctype,
				"reference": frm.doc.name,
				"time": values.time,
				"date": values.datum
			},
			"async": false,
			"callback": function(response) {
				//done
			}
		});
	},
	'Arbeitszeit erfassen',
	'Erfassen'
	)
}
