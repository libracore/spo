// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

var make_default_ts_entry = false;

frappe.ui.form.on('Vollmacht', {
	onload: function(frm) {
		check_todesfall(frm);
		set_kunden_html(frm);
		set_ang_html(frm);
		set_begleitbrief(frm);
		if (cur_frm.is_new()) {
			make_default_ts_entry = true;
		}
	},
	before_save: function(frm) {
		/* if (!cur_frm.doc.titelzeile && !cur_frm.doc.todesfall) {
			var titelzeile_string = '<p><b>Abklärungen im Zusammenhang mit</b> (dem Eingriffes/ der Operation) <b>vom</b> (Datum)  <b>im Spital XY</b> (Ort) <b>samt</b> (Folgen) oder (inkl. Vor- und Nachbehandlung)<b>.</b></p>';
			cur_frm.set_value('titelzeile', titelzeile_string);
		} else if (!cur_frm.doc.titelzeile && cur_frm.doc.todesfall) {
			var titelzeile_string = '<p><b>Abklärung der medizinischen Behandlung vom</b> (Datum) <b>im Spital XY</b> (Ort) <b>samt Folgen im Zusammenhang mit dem Todesfall betreffend Herrn/Frau/des Kindes</b> (fett: † Name, geb*   – gest., Adresse) <b>insbesondere vollständige Einsicht in die damit verbundenen Akten.</b></p>';
			cur_frm.set_value('titelzeile', titelzeile_string);
		} */
	},
	refresh: function(frm) {
		// timer action icon
		cur_frm.page.add_action_icon(__("fa fa-history"), function() {
			timesheet_handling(frm);
		});
		
		if (!cur_frm.is_new()&&make_default_ts_entry) {
			frappe.call({
				"method": "spo.utils.timesheet_handlings.handle_timesheet",
				"args": {
					"user": frappe.session.user_email,
					"doctype": frm.doc.doctype,
					"reference": frm.doc.name,
					"time": 0.00,
					"date": frappe.datetime.now_date()
				},
				"async": false,
				"callback": function(response) {
					//done
				}
			});
			make_default_ts_entry = false;
		}
		
		
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
		
		set_titelzeile(frm);
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
	if (!cur_frm.doc.daten_von_hand) {
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
						cur_frm.set_value("plz", adresse.plz);
						cur_frm.set_value("wohnort", adresse.city);
						if (kontakt.phone) {
							cur_frm.set_value("telefon", kontakt.phone);
						} else if (kontakt.mobile_no) {
							cur_frm.set_value("telefon", kontakt.mobile_no);
						}
						if (!cur_frm.doc.adressat) {
							cur_frm.set_value("adressat", kontakt.first_name + " " + kontakt.last_name + "\n" + adresse.address_line1 + "\n" + adresse.plz + " " + adresse.city);
						}
					}
				}
			});
		}
	}
}

function fetch_data_from_kunde(frm) {
	if (!cur_frm.doc.daten_von_hand) {
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
						cur_frm.set_value("plz", adresse.plz);
						cur_frm.set_value("wohnort", adresse.city);
						if (kontakt.phone) {
							cur_frm.set_value("telefon", kontakt.phone);
						} else if (kontakt.mobile_no) {
							cur_frm.set_value("telefon", kontakt.mobile_no);
						}
						if (!cur_frm.doc.adressat) {
							cur_frm.set_value("adressat", kontakt.first_name + " " + kontakt.last_name + "\n" + adresse.address_line1 + "\n" + adresse.plz + " " + adresse.city);
						}
					}
				}
			});
		}
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
				if (cur_frm.doc.todesfall == 1) {
					fetch_data_from_ang(frm);
				} else {
					fetch_data_from_kunde(frm);
				}
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
				if (cur_frm.doc.todesfall == 1) {
					fetch_data_from_ang(frm);
				} else {
					fetch_data_from_kunde(frm);
				}
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

function set_begleitbrief(frm) {
	if (!cur_frm.doc.begleitbrief) {
		var begleitbrief = '';
		begleitbrief += '<p>Sehr geehrte ...</p>';
		begleitbrief += '<p>Wir wenden uns schriftlich an Sie, da wir Sie telefonisch nicht erreichen konnten.</p>';
		begleitbrief += '<p>Wir wurden von Ihrer Rechtsschutzversicherung (Name der Vers.)  beauftragt die Behandlung vom (Datum und wer/wo) abzuklären.';
		begleitbrief += 'Damit wir aktiv werden können, sende ich Ihnen die Vollmacht zur Unterschrift. Bitte prüfen Sie das Formular insbesondere das Fettgedruckte auf die Richtigkeit und schicken Sie nach Unterschrift ein Exemplar im beigelegten Couvert wieder zurück an die SPO.';
		begleitbrief += 'Eine Vollmacht gilt als Kopie und geht zu ihren Akten.</p>';
		begleitbrief += '<p>Ich wäre sehr froh, wenn Sie mich telefonisch kontaktieren könnten. Sie erreichen mich jeweils mittwochs (10-12 Uhr und 14-16 Uhr) im Büro Zürich unter der Tel. Nr.: 044 252 522.</p>';
		begleitbrief += '<p>Freundliche Grüsse<br><br><br></p>';
		begleitbrief += '<p>... ...<br>Beratung SPO</p>';
		cur_frm.set_value("begleitbrief", begleitbrief);
	}
}

function set_titelzeile(frm) {
	if ((!cur_frm.doc.titelzeile && !cur_frm.doc.todesfall)||(cur_frm.doc.titelzeile == '<div><br></div>' && !cur_frm.doc.todesfall)) {
		var titelzeile_string = '<p><b>Abklärungen im Zusammenhang mit</b> (dem Eingriffes/ der Operation) <b>vom</b> (Datum)  <b>im Spital XY</b> (Ort) <b>samt</b> (Folgen) oder (inkl. Vor- und Nachbehandlung)<b>.</b></p>';
		cur_frm.set_value('titelzeile', titelzeile_string);
	} else if ((!cur_frm.doc.titelzeile && cur_frm.doc.todesfall)||(cur_frm.doc.titelzeile == '<div><br></div>' && cur_frm.doc.todesfall)) {
		var titelzeile_string = '<p><b>Abklärung der medizinischen Behandlung vom</b> (Datum) <b>im Spital XY</b> (Ort) <b>samt Folgen im Zusammenhang mit dem Todesfall betreffend Herrn/Frau/des Kindes</b> (fett: † Name, geb*   – gest., Adresse) <b>insbesondere vollständige Einsicht in die damit verbundenen Akten.</b></p>';
		cur_frm.set_value('titelzeile', titelzeile_string);
	}
}
