// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

// mitgliedschaft = Mitgliedschaft (Typ, Von, Bis)
// mitglied = Kunde
// mitgliedernummer = Kundennummer

frappe.ui.form.on('Anfrage', {
	onload: function(frm) {
		if (frm.doc.__islocal) {
			cur_frm.doc.mitglied = '';
			cur_frm.set_value('datum', frappe.datetime.get_today());
			cur_frm.set_value('patient', cur_frm.doc.customer);
			nothing_mandatory(frm);
			cur_frm.save();
		}
	},
	refresh: function(frm) {
		//dropdown steuerung von sections
		dropdown_steuerung_von_sections(frm);
				
		//load dashboard
		if (frm.doc.anfrage_typ == __('Sonstiges')) {
			update_dashboard(frm);
		}
		
		// timer action icon
		cur_frm.page.add_action_icon(__("fa fa-history"), function() {
			timesheet_handling(frm);
		});
		
		//add btn to create Mandat
		if (cur_frm.doc.patient) {
			frappe.call({
				method:"frappe.client.get_list",
				args:{
					doctype:"Anfrage",
					filters: [
						["mitglied","=", cur_frm.doc.patient]
					],
					fields: ["name"],
					order_by: 'creation'
				},
				callback: function(r) {
					if (r.message.length > 0) {
						if (r.message[(r.message.length - 1)].name == frm.doc.name) {
							frm.add_custom_button(__("Mandat"), function() {
								new_mandat(frm.doc.name, frm.doc.patient, frm.doc.patienten_adresse, frm.doc.patienten_kontakt);
							});
						}
					} else {
						frm.add_custom_button(__("Mandat"), function() {
							new_mandat(frm.doc.name, frm.doc.patient, frm.doc.patienten_adresse, frm.doc.patienten_kontakt);
						});
					}
				}
			});
		} else {
			frm.add_custom_button(__("Mandat"), function() {
				new_mandat(frm.doc.name, frm.doc.patient, frm.doc.patienten_adresse, frm.doc.patienten_kontakt);
			});
		}
		
		//Set filter to link fields
		set_link_filter(frm);
		
		//prüfen ob Mitgliedschaft gültig ist und ob die Rechnung bezahlt ist
		if (frm.doc.mitgliedschaft) {
			check_mitgliedschaft_ablaufdatum(frm);
			check_rechnung(frm);
		} else {
			frm.add_custom_button(__("Keine Mitgliedschaft hinterlegt"), function() {
				
			}).addClass("btn-info pull-left");
		}
		
		//pflichtfelder basierend auf Anfrage Typ
		set_mandatory_and_read_only(frm);
		
		
		//*************************************************************************
		// vorübergehend deaktiviert
		//überprüfung ob kontakt- und adress-daten mit stamm übereinstimmen
		//check_anfrage_daten_vs_stamm_daten(frm);
		//*************************************************************************
		
		//update timesheet table
		frappe.call({
			"method": "spo.spo.doctype.anfrage.anfrage.create_zeiten_uebersicht",
			"args": {
				"dt": cur_frm.doctype,
				"name": cur_frm.doc.name
			},
			"async": false,
			"callback": function(r) {
				if (r.message) {
					cur_frm.set_df_property('zeiten_uebersicht','options', r.message);
					$("[data-funktion='open_ts']").on('click', function() {
						ts_bearbeiten($(this).attr("data-referenz"));
					});
				}
			}
		});
	},
	anfrage_typ: function(frm) {
		//pflichtfelder basierend auf Anfrage Typ
		cur_frm.set_value('kontakt_via', '');
		set_mandatory_and_read_only(frm);
	},
	anonymisiert: function(frm) {
		//pflichtfelder basierend auf Anfrage Typ
		set_mandatory_and_read_only(frm);
	},
	problematik: function(frm) {
		//pflichtfelder basierend auf Anfrage Typ
		set_mandatory_and_read_only(frm);
	},
	patient: function(frm) {
		if (cur_frm.doc.patient) {
			frappe.call({
				method:"frappe.client.get_list",
				args:{
					doctype:"Anfrage",
					filters: [
						["patient","=", cur_frm.doc.patient]
					],
					fields: ["name"],
					order_by: 'creation'
				},
				callback: function(r) {
					if (r.message.length > 0) {
						if (r.message[(r.message.length - 1)].name == frm.doc.name) {
							frm.add_custom_button(__("Mandat"), function() {
								new_mandat(frm.doc.name, frm.doc.patient, frm.doc.patienten_adresse, frm.doc.patienten_kontakt);
							});
						} else {
							cur_frm.remove_custom_button("Mandat");
						}
					}
				}
			});
		} else {
			frm.add_custom_button(__("Mandat"), function() {
				new_mandat(frm.doc.name, frm.doc.patient, frm.doc.patienten_adresse, frm.doc.patienten_kontakt);
			});
		}
		//cur_frm.scroll_to_field("mitgliedschaft");
		
			cur_frm.set_value('customer', cur_frm.doc.patient);
	},
	mitglied_erstellen: function(frm) {
		frappe.call({
			method:"frappe.core.doctype.user.user.get_roles",
			args: {"uid":frappe.user.name}
		}).done((r)=>{
			var i;
			var has_role = false;
			for (i=0; i < r.message.length; i++) {
				if (r.message[i] == __("Backoffice")) {
					has_role = true;
				}
			}
			if (has_role) {
				//kontrolle ob pflichtfelder ausgefüllt
				var fehlende_daten = '';
				var fehler = false;
				if(!frm.doc.patient_vorname) {
					fehlende_daten += 'Vorname<br>';
					fehler = true;
				}
				if(!frm.doc.patient_nachname) {
					fehlende_daten += 'Nachname<br>';
					fehler = true;
				}
				if(!frm.doc.patient_strasse) {
					fehlende_daten += 'Strasse<br>';
					fehler = true;
				}
				if(!frm.doc.patient_plz) {
					fehlende_daten += 'Postleitzahl<br>';
					fehler = true;
				}
				
				var mail = ''
				if (frm.doc.patient_mail) {
					if (frm.doc.patient_mail.split("@").length == 2) {
						if (frm.doc.patient_mail.split("@")[1].split(".").length == 2) {
							if (frm.doc.patient_mail.split("@")[1].split(".")[1] != '') {
								mail = frm.doc.patient_mail;
							}
						}
					}
				}
				if (fehler) {
					frappe.msgprint(__("Bitte tragen Sie mindestens noch folgende Daten ein:<br>") + fehlende_daten, __("Fehlende Daten"));
				} else {
					frappe.call({
						"method": "spo.spo.doctype.anfrage.anfrage.create_new_mitglied",
						"args": {
							"vorname": frm.doc.patient_vorname,
							"nachname": frm.doc.patient_nachname,
							"strasse": frm.doc.patient_strasse,
							"adress_zusatz": frm.doc.patient_adress_zusatz,
							"ort": frm.doc.patient_ort,
							"plz": frm.doc.patient_plz,
							"email": mail,
							"telefon": frm.doc.patient_telefon,
							"mobile": frm.doc.patient_mobile,
							"geburtsdatum": frm.doc.patient_geburtsdatum,
							"kanton": frm.doc.patient_kanton
						},
						"async": false,
						"callback": function(r) {
							if (r.message) {
								cur_frm.set_value('patient', r.message.patient);
								cur_frm.set_value('patienten_kontakt', r.message.patienten_kontakt);
								cur_frm.set_value('patienten_adresse', r.message.patienten_adresse);
								nothing_mandatory(frm);
								cur_frm.save();
								frappe.msgprint(__("Das Mitglied <b>") + r.message.patient + __("</b> wurde angelegt<br><br>Bitte erfassen Sie noch die entsprechende Mitgliedschaft."), __("Mitglied wurde angelegt"));
							}
						}
					});
				}
			} else {
				frappe.call({
					method: 'spo.spo.doctype.anfrage.anfrage.assign_mitglied_anlage',
					callback: function(r) {
						if(r.message) {
							//auto assign
							nothing_mandatory(frm);
							cur_frm.save();
							assign_anfrage(frm, r.message, '', false);
						} 
					}
				});
			}
		});
	},
	scroll_top_0: function(frm) {
		frappe.utils.scroll_to(0);
		cur_frm.fields[5].collapse_link.click();
	},
	scroll_top_1: function(frm) {
		frappe.utils.scroll_to(0);
		cur_frm.fields[29].collapse_link.click();
	},
	scroll_top_2: function(frm) {
		frappe.utils.scroll_to(0);
		cur_frm.fields[51].collapse_link.click();
	},
	scroll_top_3: function(frm) {
		frappe.utils.scroll_to(0);
		cur_frm.fields[56].collapse_link.click();
	},
	patient_plz: function(frm) {
		get_city_from_pincode(cur_frm.doc.patient_plz, 'patient_ort', 'patient_kanton');
	},
	ang_plz: function(frm) {
		get_city_from_pincode(cur_frm.doc.ang_plz, 'ang_ort', 'ang_kanton');
	},
	ges_ver_1_plz: function(frm) {
		get_city_from_pincode(cur_frm.doc.ges_ver_1_plz, 'ges_ver_1_ort', 'ges_ver_1_kanton');
	},
	ges_ver_2_plz: function(frm) {
		get_city_from_pincode(cur_frm.doc.ges_ver_2_plz, 'ges_ver_2_ort', 'ges_ver_2_kanton');
	},
	absprung_einstellungen: function(frm) {
		frappe.set_route("Form", "Einstellungen");
	},
	kontaktdaten_suchen: function(frm) {
		_kontaktdaten_suchen(frm);
	},
	rsv: function(frm) {
		fetch_rsv(frm);
	},
	rsv_kontakt: function(frm) {
		fetch_rsv(frm);
	},
	rsv_adresse: function(frm) {
		fetch_rsv(frm);
	}
});

function new_mandat(anfrage, patient, adresse, kontakt) {
	if (patient) {
		frappe.call({
			method: 'spo.spo.doctype.anfrage.anfrage.creat_new_mandat',
			args: {
				'anfrage': anfrage,
				'mitglied': patient,
				'adresse': adresse,
				'kontakt': kontakt,
				'rsv': cur_frm.doc.rsv,
				'rsv_kontakt': cur_frm.doc.rsv_kontakt,
				'rsv_adresse': cur_frm.doc.rsv_adresse,
				'rsv_ref': cur_frm.doc.rechtsschutz_ref,
				'ang': cur_frm.doc.ang,
				'ang_kontakt': cur_frm.doc.ang_kontakt,
				'ang_adresse': cur_frm.doc.ang_adresse,
				'ges_ver_1': cur_frm.doc.ges_ver_1,
				'ges_ver_1_adresse': cur_frm.doc.ges_ver_1_address,
				'ges_ver_1_kontakt': cur_frm.doc.ges_ver_1_contact,
				'ges_ver_2': cur_frm.doc.ges_ver_2,
				'ges_ver_2_adresse': cur_frm.doc.ges_ver_2_address,
				'ges_ver_2_kontakt': cur_frm.doc.ges_ver_2_contact
			},
			callback: function(r) {
				if(r.message) {
					if (r.message != 'already exist') {
						frappe.set_route("Form", "Mandat", r.message)
					} else {
						frappe.confirm(
							__('Zu dieser Anfrage wurde bereits ein Mandat eröffnet.<br><br>Soll das/die Mandat(e) angezeigt werden?'),
							function(){
								// on yes
								show_mandat_list_based_on_anfrage();
							},
							function(){
								// on no --> close popup
							}
						);
					}
				} 
			}
		});
	} else {
		frappe.msgprint(__("Bitte tragen Sie zuerst einen Kunden ein."), __("Fehlender Kunde"));
	}
}

function show_mandat_list_based_on_anfrage() {
	frappe.route_options = {"anfragen": ["like", "%" + cur_frm.doc.name + "%"]};
	frappe.set_route("List", "Mandat");
}

function get_valid_mitgliedschaft_based_on_mitgliedernummer(frm, patient) {
	frappe.call({
        "method": "spo.spo.doctype.anfrage.anfrage.get_valid_mitgliedschaft_based_on_mitgliedernummer",
        "args": {
            "mitgliedernummer": patient
        },
        "async": false,
        "callback": function(r) {
            if (r.message.length >= 1) {
				cur_frm.set_value('mitgliedschaft', r.message[0].name);
				if (r.message.length > 1) {
					frappe.msgprint(__("<b>Achtung!</b><br>Das Mitglied besitzt mehere gültige Mitgliedschaften, bitte prüfen Sie die autom. Selektion!"), __("Mehrere gültige Mitgliedschaften"));
				}
			} else {
				frappe.msgprint(__("<b>Achtung!</b><br>Das Mitglied besitzt keine gültige Mitgliedschaft!"), __("Keine gültige Mitgliedschaft"));
			}
        }
    });
}

function check_mitgliedschaft_ablaufdatum(frm) {
	if (frm.doc.mitgliedschaft) {
		frappe.call({
			"method": "spo.spo.doctype.anfrage.anfrage.check_mitgliedschaft_ablaufdatum",
			"args": {
				"mitgliedschaft": frm.doc.mitgliedschaft
			},
			"async": false,
			"callback": function(response) {
				if (!response.message) {
					frappe.msgprint(__("Die hinterlegte Mitgliedschaft ist abgelaufen!"), __('Achtung'));
				}
			}
		});
	}
}

function update_dashboard(frm) {
	frappe.call({
		"method": "spo.spo.doctype.anfrage.anfrage.get_dashboard_data",
		"args": {
			"mitglied": frm.doc.patient,
			"anfrage": frm.doc.name
		},
		"async": true,
		"callback": function(response) {
			var query = response.message;
			//Limits
			var _colors = ['#d40000', '#00b000'];
			/* if (query.callcenter_verwendet == 0) {
				_colors = ['#00b000', '#d40000'];
			} */
			let limit_chart = new frappe.Chart( "#limit", { // or DOM element
				data: {
				labels: [__("Verwendet"), __("Ausstehend")],

				datasets: [
					{
						values: [query.callcenter_verwendet, query.callcenter_limit - query.callcenter_verwendet]
					}
				],

				},
				title: __("Zeitauswertung (in min)"),
				type: 'percentage', // or 'bar', 'line', 'pie', 'percentage'
				colors: _colors,
				barOptions: {
					height: 20,          // default: 20
					depth: 0             // default: 2
				}
			});
			
			if (query.mitgliedschaften != 'keine') {
				check_mitgliedschafts_unterbruch(frm, query.mitgliedschaften, query.limite_unterbruch);
			}
		}
	});
}

function check_rechnung(frm) {
	frappe.call({
		"method": "spo.spo.doctype.anfrage.anfrage.check_rechnung",
		"args": {
			"mitgliedschaft": frm.doc.mitgliedschaft
		},
		"async": false,
		"callback": function(response) {
			var rechnung = response.message;
			if (rechnung == "Keine Rechnung") {
				frm.add_custom_button(__("Es wurde noch keine Mitgliederrechnung erstellt!"), function() {
					
				}).addClass("btn-danger pull-left");
			} else if (rechnung == "Paid") {
				frm.add_custom_button(__("Die Mitgliederrechnung wurde bezahlt."), function() {
					
				}).addClass("btn-success pull-left");
			} else {
				frm.add_custom_button(__("Die Mitgliederrechnung ist unbezahlt!"), function() {
					
				}).addClass("btn-warning pull-left");
			}
		}
	});
}

function scroll_to(where) {
	frappe.utils.scroll_to(where, !0);
}

function check_mitgliedschafts_unterbruch(frm, mitgliedschaften, limite_unterbruch) {
	if (mitgliedschaften.length >= 1) {
		var i;
		var mitgliedschafts_diff = false;
		
		for (i=0; i<mitgliedschaften.length - 1; i++) {
			if (frappe.datetime.get_day_diff(mitgliedschaften[i + 1].start, mitgliedschaften[i].ende) > limite_unterbruch) {
				mitgliedschafts_diff = true;
			}
		}
		
		if (mitgliedschafts_diff) {
			frm.add_custom_button(__("Mitglied seit ") + frappe.datetime.obj_to_user(mitgliedschaften[0].start) + ' <i class="fa fa-exclamation-circle"></i>', function() {
				show_unterbruch(mitgliedschaften);
			}).addClass("btn-warning pull-left");
		} else {
			frm.add_custom_button(__("Mitglied seit ") + frappe.datetime.obj_to_user(mitgliedschaften[0].start), function() {
				show_unterbruch(mitgliedschaften);
			}).addClass("btn-success pull-left");
		}
	}
}

function show_unterbruch(mitgliedschaften) {
	var table = '<table style="width: 100%;"><tr><th>' + __("Mitgliedschaft") + '</th><th>' + __("Start") + '</th><th>' + __("Ende") + '</th></tr>';
	var i;
	
	for (i=0; i < mitgliedschaften.length; i++) {
		table += '<tr><td><a target="_blank" href="/desk#Form/Mitgliedschaft/' + mitgliedschaften[i].name + '">' + mitgliedschaften[i].name + '</a></td><td>' + frappe.datetime.obj_to_user(mitgliedschaften[i].start) + '</td><td>' + frappe.datetime.obj_to_user(mitgliedschaften[i].ende) + '</td></tr>';
	}
	
	table += '</table>';
	
	frappe.msgprint(table, __("Übersicht der Mitgliedschaften"));
}

function set_mandatory_and_read_only(frm) {
	if (!frm.doc.__islocal) {
		cur_frm.set_df_property('patient_kanton','reqd', 1);
		cur_frm.set_df_property('problematik','reqd', 0);
		if (frm.doc.anfrage_typ == __('Hotline') || frm.doc.anfrage_typ == __('Medien Anfrage')) {
			if (frm.doc.anfrage_typ == __('Hotline')) {
				cur_frm.set_value('kontakt_via', __('Telefon'));
				cur_frm.set_df_property('kontakt_via','read_only', 1);
			} else {
				cur_frm.set_df_property('kontakt_via','read_only', 0);
			}
			cur_frm.set_df_property('patient_vorname','reqd', 0);
			cur_frm.set_df_property('patient_nachname','reqd', 0);
			cur_frm.set_df_property('patient_geburtsdatum','reqd', 0);
			cur_frm.set_df_property('patient_kanton','reqd', 0);
			cur_frm.set_df_property('patient_strasse','reqd', 0);
			cur_frm.set_df_property('patient_ort','reqd', 0);
			cur_frm.set_df_property('patient_plz','reqd', 0);
			cur_frm.set_df_property('patient_mail','reqd', 0);
			cur_frm.set_df_property('problematik','reqd', 1);
			if (frm.doc.anonymisiert == 1) {
				cur_frm.set_df_property('patient_kanton','reqd', 1);
				cur_frm.set_df_property('patient_nachname','reqd', 0);
			} else {
				cur_frm.set_df_property('patient_kanton','reqd', 1);
				cur_frm.set_df_property('patient_nachname','reqd', 1);
			}
		} else {
			cur_frm.set_df_property('kontakt_via','read_only', 0);
			cur_frm.set_df_property('patient_vorname','reqd', 1);
			cur_frm.set_df_property('patient_nachname','reqd', 1);
			cur_frm.set_df_property('patient_geburtsdatum','reqd', 1);
			cur_frm.set_df_property('patient_kanton','reqd', 1);
			cur_frm.set_df_property('patient_strasse','reqd', 1);
			cur_frm.set_df_property('patient_ort','reqd', 1);
			cur_frm.set_df_property('patient_plz','reqd', 1);
			cur_frm.set_df_property('patient_mail','reqd', 1);
			cur_frm.set_df_property('spo_ombudsstelle','reqd', 1);
			cur_frm.set_df_property('kontakt_via','reqd', 1);
			
			if (frm.doc.anfrage_typ == __('Mandats Anfrage')) {
				cur_frm.set_df_property('patient_vorname','reqd', 0);
				cur_frm.set_df_property('patient_nachname','reqd', 0);
				cur_frm.set_df_property('patient_geburtsdatum','reqd', 0);
				cur_frm.set_df_property('patient_kanton','reqd', 0);
				cur_frm.set_df_property('patient_strasse','reqd', 0);
				cur_frm.set_df_property('patient_ort','reqd', 0);
				cur_frm.set_df_property('patient_plz','reqd', 0);
				cur_frm.set_df_property('patient_mail','reqd', 0);
				cur_frm.set_df_property('patient_kanton','reqd', 0);
				cur_frm.set_df_property('patient_nachname','reqd', 0);
				//cur_frm.set_df_property('problematik','hidden', 1);
				cur_frm.set_df_property('spo_ombudsstelle','reqd', 1);
			}
		}
		if (cur_frm.doc.problematik == __('Krankenkasse (Grundversicherung)')) {
			cur_frm.set_df_property('krankenkasse','reqd', 1);
		}
	}
}

function nothing_mandatory(frm) {
	cur_frm.set_df_property('problematik','reqd', 0);
	cur_frm.set_df_property('patient_nachname','reqd', 0);
	cur_frm.set_df_property('patient_kanton','reqd', 0);
	cur_frm.set_df_property('spo_ombudsstelle','reqd', 0);
	cur_frm.set_df_property('kontakt_via','reqd', 0);
	cur_frm.set_df_property('patient_vorname','reqd', 0);
	cur_frm.set_df_property('patient_geburtsdatum','reqd', 0);
	cur_frm.set_df_property('patient_strasse','reqd', 0);
	cur_frm.set_df_property('patient_ort','reqd', 0);
	cur_frm.set_df_property('patient_plz','reqd', 0);
	cur_frm.set_df_property('patient_mail','reqd', 0);
	cur_frm.set_df_property('anfrage_typ','reqd', 0);
}

function check_anfrage_daten_vs_stamm_daten(frm) {
	var i;
	var assign = true;
	if (cur_frm.get_docinfo().assignments) {
		for (i=0; i < cur_frm.get_docinfo().assignments.length; i++) {
			if (cur_frm.get_docinfo().assignments[i].description.includes(__("Bitte folgende Änderungen in den Stammdaten vornehmen:"))) {
				assign = false;
			}
		}
	}
	if (frm.doc.patient && frm.doc.patienten_kontakt && frm.doc.patienten_adresse && assign) {
		frappe.call({
			"method": "spo.spo.doctype.anfrage.anfrage.check_anfrage_daten_vs_stamm_daten",
			"args": {
				"patient": frm.doc.patient,
				"kontakt": frm.doc.patienten_kontakt,
				"adresse": frm.doc.patienten_adresse,
				"vorname": frm.doc.patient_vorname || '',
				"nachname": frm.doc.patient_nachname || '',
				"geburtsdatum": frm.doc.patient_geburtsdatum || '',
				"kanton": frm.doc.patient_kanton || '',
				"strasse": frm.doc.patient_strasse || '',
				"adress_zusatz": frm.doc.patient_adress_zusatz || '',
				"ort": frm.doc.patient_ort || '',
				"plz": frm.doc.patient_plz || '',
				"telefon": frm.doc.patient_telefon || '',
				"mobile": frm.doc.patient_mobile || '',
				"email": frm.doc.patient_mail || ''
			},
			"callback": function(response) {
				var abweichungen = response.message.abweichungen;
				var assign_to = response.message.assign_to;
				if (abweichungen != '') {
					frappe.confirm(
						__('<p>Sollen folgende Änderungen der zuständigen Abteilung zur Verarbeitung übergeben werden?</p>') + abweichungen,
						function(){
							// on yes assign
							assign_anfrage(frm, assign_to, abweichungen, true);
						},
						function(){
							// on no nothing
						}
					)
					
				}
			}
		});
	}
}

function assign_anfrage(frm, assign_to, abweichungen, mutation) {
	if (mutation) {
		frappe.call({
			"method": "frappe.desk.form.assign_to.add",
			"args": {
				"assign_to": assign_to,
				"doctype": frm.doc.doctype,
				"name": frm.doc.name,
				"description": __("Bitte folgende Änderungen in den Stammdaten vornehmen:<br>") + abweichungen
			},
			"callback": function(response) {
				frappe.msgprint(__("Die Stammdaten Änderung wurde zugewiesen."), __("Zuweisung erfolgreich"));
				nothing_mandatory(frm);
				cur_frm.save();
				cur_frm.reload_doc();
			}
		});
	} else {
		frappe.call({
			"method": "frappe.desk.form.assign_to.add",
			"args": {
				"assign_to": assign_to,
				"doctype": frm.doc.doctype,
				"name": frm.doc.name,
				"description": __("Bitte Kundenstamm anlegen.")
			},
			"callback": function(response) {
				frappe.msgprint(__("Die Stammdaten Anlage wurde zugewiesen."), __("Zuweisung erfolgreich"));
				nothing_mandatory(frm);
				cur_frm.save();
				cur_frm.reload_doc();
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

function set_link_filter(frm) {
	cur_frm.fields_dict['patienten_kontakt'].get_query = function(doc) {
		return {
			filters: {
				"link_doctype": "Customer",
				"link_name": frm.doc.patient
			}
		}
	};
	cur_frm.fields_dict['patienten_adresse'].get_query = function(doc) {
		return {
			filters: {
				"link_doctype": "Customer",
				"link_name": frm.doc.patient
			}
		}
	};
	cur_frm.fields_dict['rsv_kontakt'].get_query = function(doc) {
		return {
			filters: {
				"link_doctype": "Customer",
				"link_name": frm.doc.rsv
			}
		}
	};
	cur_frm.fields_dict['rsv_adresse'].get_query = function(doc) {
		return {
			filters: {
				"link_doctype": "Customer",
				"link_name": frm.doc.rsv
			}
		}
	};
	cur_frm.fields_dict['ang_adresse'].get_query = function(doc) {
		return {
			filters: {
				"link_doctype": "Customer",
				"link_name": frm.doc.ang
			}
		}
	};
	cur_frm.fields_dict['ang_kontakt'].get_query = function(doc) {
		return {
			filters: {
				"link_doctype": "Customer",
				"link_name": frm.doc.ang
			}
		}
	};
	cur_frm.fields_dict['mitgliedschaft'].get_query = function(doc) {
		 return {
			 filters: {
				 "mitglied": frm.doc.patient
			 }
		 }
	};
	cur_frm.fields_dict['ges_ver_1_address'].get_query = function(doc) {
		return {
			filters: {
				"link_doctype": "Customer",
				"link_name": frm.doc.ges_ver_1
			}
		}
	};
	cur_frm.fields_dict['ges_ver_1_contact'].get_query = function(doc) {
		return {
			filters: {
				"link_doctype": "Customer",
				"link_name": frm.doc.ges_ver_1
			}
		}
	};
	cur_frm.fields_dict['ges_ver_2_address'].get_query = function(doc) {
		return {
			filters: {
				"link_doctype": "Customer",
				"link_name": frm.doc.ges_ver_2
			}
		}
	};
	cur_frm.fields_dict['ges_ver_2_contact'].get_query = function(doc) {
		return {
			filters: {
				"link_doctype": "Customer",
				"link_name": frm.doc.ges_ver_2
			}
		}
	};
}

function _kontaktdaten_suchen(frm) {
	var vorname = cur_frm.doc.patient_vorname;
	var nachname = cur_frm.doc.patient_nachname;
	var strasse = cur_frm.doc.patient_strasse;
	var adress_zusatz = cur_frm.doc.patient_adress_zusatz;
	var plz = cur_frm.doc.patient_plz;
	var ort = cur_frm.doc.patient_ort;
	var kanton = cur_frm.doc.patient_kanton;
	var mail = cur_frm.doc.patient_mail;
	var telefon = cur_frm.doc.patient_telefon;
	var mobile = cur_frm.doc.patient_mobile;
	var geburtsdatum = cur_frm.doc.patient_geburtsdatum;
	
	frappe.call({
		"method": "spo.spo.doctype.anfrage.anfrage.kontaktdaten_suchen",
		"args": {
			'vorname': vorname,
			'nachname': nachname,
			'strasse': strasse,
			'adress_zusatz': adress_zusatz,
			'plz': plz,
			'ort': ort,
			'kanton': kanton,
			'mail': mail,
			'telefon': telefon,
			'mobile': mobile,
			'geburtsdatum': geburtsdatum
		},
		"callback": function(r) {
			if (r.message) {
				var full_matches = r.message.full_matches;
				var alle_kontakte = r.message.alle_kontakte;
				var alle_adressen = r.message.alle_adressen;
				
				var d = new frappe.ui.Dialog({
					'fields': [
						{'fieldname': 'header_1', 'fieldtype': 'Heading', 'label': __('Vollständige Treffer')},
						{'fieldname': 'full_matches', 'fieldtype': 'HTML', 'options': __('<div><p>Keine vollständige Treffer</p></div>')},
						{'fieldname': 'header_2', 'fieldtype': 'Heading', 'label': __('Zutreffende Kontakte')},
						{'fieldname': 'alle_kontakte', 'fieldtype': 'HTML', 'options': __('<div><p>Keine zutreffende Kontakte</p></div>')},
						{'fieldname': 'header_3', 'fieldtype': 'Heading', 'label': __('Zutreffende Adressen')},
						{'fieldname': 'alle_adressen', 'fieldtype': 'HTML', 'options': __('<div><p>Keine zutreffende Adressen</p></div>')}
					],
					primary_action: function(){
						fetch_match_from_dialog(frm, d);
					},
					primary_action_label: __('Daten übernehmen')
				});
				//full matches
				if (full_matches.length > 0) {
					var full_matches_html = '<div class="row">';
					var i;
					for (i=0; i < full_matches.length; i++) {
						full_matches_html += '<div class="col-sm-4">';
						full_matches_html += '<div class="radio">';
						full_matches_html += '<label><input type="radio" name="optradio" data-match="full" data-customer="' + full_matches[i].kunde + '" data-adresse="' + full_matches[i].adressen[0].name + '" data-kontakt="' + full_matches[i].kontakte[0].name + '">Auswählen</label>';
						full_matches_html += '</div>';
						full_matches_html += '</div>';
						
						full_matches_html += '<div class="col-sm-4">';
						full_matches_html += full_matches[i].kontakte[0].first_name + " " + full_matches[i].kontakte[0].last_name + "<br>";
						full_matches_html += full_matches[i].kontakte[0].geburtsdatum + "<br>";
						full_matches_html += full_matches[i].kontakte[0].email_id + "<br>";
						full_matches_html += full_matches[i].kontakte[0].phone + "<br>";
						full_matches_html += full_matches[i].kontakte[0].mobile_no + "<br>";
						full_matches_html += '</div>';
						full_matches_html += '<div class="col-sm-4">';
						full_matches_html += full_matches[i].adressen[0].address_line1 + "<br>";
						full_matches_html += full_matches[i].adressen[0].address_line2 + "<br>";
						full_matches_html += full_matches[i].adressen[0].plz + " " + full_matches[i].adressen[0].city + " " + full_matches[i].adressen[0].kanton;
						full_matches_html += '</div>';
						full_matches_html += '<div class="col-sm-12"><hr></div>';
					}
					full_matches_html += '</div>';
					d.fields_dict.full_matches.$wrapper.html(full_matches_html);
				}
				
				//kontakte
				if (alle_kontakte.length > 0) {
					var alle_kontakte_html = '<div class="row">';
					var i;
					for (i=0; i < alle_kontakte.length; i++) {
						alle_kontakte_html += '<div class="col-sm-4">';
						alle_kontakte_html += '<div class="radio">';
						alle_kontakte_html += '<label><input type="radio" name="optradio" data-match="kontakt" data-customer="' + alle_kontakte[i].kunde[0].link_name + '" data-kontakt="' + alle_kontakte[i].kontakt[0].name + '">Auswählen</label>';
						alle_kontakte_html += '</div>';
						alle_kontakte_html += '</div>';
						
						alle_kontakte_html += '<div class="col-sm-8">';
						alle_kontakte_html += alle_kontakte[i].kontakt[0].first_name + " " + alle_kontakte[i].kontakt[0].last_name + "<br>";
						alle_kontakte_html += alle_kontakte[i].kontakt[0].geburtsdatum + "<br>";
						alle_kontakte_html += alle_kontakte[i].kontakt[0].email_id + "<br>";
						alle_kontakte_html += alle_kontakte[i].kontakt[0].phone + "<br>";
						alle_kontakte_html += alle_kontakte[i].kontakt[0].mobile_no;
						alle_kontakte_html += '</div>';
						alle_kontakte_html += '<div class="col-sm-12"><hr></div>';
					}
					alle_kontakte_html += '</div>';
					d.fields_dict.alle_kontakte.$wrapper.html(alle_kontakte_html);
				}
				
				//adressen
				if (alle_adressen.length > 0) {
					var alle_adressen_html = '<div class="row">';
					var i;
					for (i=0; i < alle_adressen.length; i++) {
						alle_adressen_html += '<div class="col-sm-4">';
						alle_adressen_html += '<div class="radio">';
						alle_adressen_html += '<label><input type="radio" name="optradio" data-match="adresse" data-customer="' + alle_adressen[i].kunde[0].link_name + '" data-adresse="' + alle_adressen[i].adresse[0].name + '">Auswählen</label>';
						alle_adressen_html += '</div>';
						alle_adressen_html += '</div>';
						
						alle_adressen_html += '<div class="col-sm-8">';
						alle_adressen_html += alle_adressen[i].adresse[0].address_line1 + "<br>";
						alle_adressen_html += alle_adressen[i].adresse[0].address_line2 + "<br>";
						alle_adressen_html += alle_adressen[i].adresse[0].plz + " " + alle_adressen[i].adresse[0].city + " " + alle_adressen[i].adresse[0].kanton;
						alle_adressen_html += '</div>';
						alle_adressen_html += '<div class="col-sm-12"><hr></div>';
					}
					alle_adressen_html += '</div>';
					d.fields_dict.alle_adressen.$wrapper.html(alle_adressen_html);
				}
				
				d.show();
			}
		}
	});
}

function fetch_match_from_dialog(frm, d) {
	var all_radios = $('[name="optradio"]');
	var i;
	for (i=0; i < all_radios.length; i++) {
		if (all_radios[i].checked) {
			cur_frm.set_value('patient', $(all_radios[i]).data('customer'));
			if ($(all_radios[i]).data('match') == 'full') {
				cur_frm.set_value('patienten_adresse', $(all_radios[i]).data('adresse'));
				cur_frm.set_value('patienten_kontakt', $(all_radios[i]).data('kontakt'));
				
				frappe.db.get_value('Address', {'name': cur_frm.doc.patienten_adresse}, ['address_line1', 'address_line2', 'plz', 'city', 'kanton'], (r) => {
					cur_frm.set_value('patient_strasse', r.address_line1);
					cur_frm.set_value('patient_adress_zusatz', r.address_line2);
					cur_frm.set_value('patient_ort', r.city);
					cur_frm.set_value('patient_kanton', r.kanton);
					cur_frm.set_value('patient_plz', r.plz);
				});
				
				frappe.db.get_value('Contact', {'name': cur_frm.doc.patienten_kontakt}, ['first_name', 'last_name', 'email_id', 'phone', 'mobile_no', 'geburtsdatum'], (r) => {
					cur_frm.set_value('patient_vorname', r.first_name);
					cur_frm.set_value('patient_nachname', r.last_name);
					cur_frm.set_value('patient_mail', r.email_id);
					cur_frm.set_value('patient_telefon', r.phone);
					cur_frm.set_value('patient_mobile', r.mobile_no);
					cur_frm.set_value('patient_geburtsdatum', r.geburtsdatum);
				});
			} else if ($(all_radios[i]).data('match') == 'adresse') {
				cur_frm.set_value('patienten_adresse', $(all_radios[i]).data('adresse'));
				
				frappe.db.get_value('Address', {'name': cur_frm.doc.patienten_adresse}, ['address_line1', 'address_line2', 'plz', 'city', 'kanton'], (r) => {
					cur_frm.set_value('patient_strasse', r.address_line1);
					cur_frm.set_value('patient_adress_zusatz', r.address_line2);
					cur_frm.set_value('patient_ort', r.city);
					cur_frm.set_value('patient_kanton', r.kanton);
					cur_frm.set_value('patient_plz', r.plz);
				});
			} else if ($(all_radios[i]).data('match') == 'kontakt') {
				cur_frm.set_value('patienten_kontakt', $(all_radios[i]).data('kontakt'));
				
				frappe.db.get_value('Contact', {'name': cur_frm.doc.patienten_kontakt}, ['first_name', 'last_name', 'email_id', 'phone', 'mobile_no', 'geburtsdatum'], (r) => {
					cur_frm.set_value('patient_vorname', r.first_name);
					cur_frm.set_value('patient_nachname', r.last_name);
					cur_frm.set_value('patient_mail', r.email_id);
					cur_frm.set_value('patient_telefon', r.phone);
					cur_frm.set_value('patient_mobile', r.mobile_no);
					cur_frm.set_value('patient_geburtsdatum', r.geburtsdatum);
				});
			}
		}
	}
	
	d.hide();
}

function dropdown_steuerung_von_sections(frm) {
	if (cur_frm.fields_dict.section_anfrage && !cur_frm.fields_dict.section_anfrage.is_collapsed()) {
		cur_frm.fields_dict.section_anfrage.collapse();
	}
	if (cur_frm.fields_dict.section_dashboard && !cur_frm.fields_dict.section_dashboard.is_collapsed()) {
		cur_frm.fields_dict.section_dashboard.collapse();
	}
	if (cur_frm.fields_dict.section_kontakt_daten && !cur_frm.fields_dict.section_kontakt_daten.is_collapsed()) {
		cur_frm.fields_dict.section_kontakt_daten.collapse();
	}
	if (cur_frm.fields_dict.section_patienten_links && !cur_frm.fields_dict.section_patienten_links.is_collapsed()) {
		cur_frm.fields_dict.section_patienten_links.collapse();
	}
	if (cur_frm.fields_dict.section_person && !cur_frm.fields_dict.section_person.is_collapsed()) {
		cur_frm.fields_dict.section_person.collapse();
	}
	if (cur_frm.fields_dict.section_angehoerige && !cur_frm.fields_dict.section_angehoerige.is_collapsed()) {
		cur_frm.fields_dict.section_angehoerige.collapse();
	}
	if (cur_frm.fields_dict.section_angehoerige_links && !cur_frm.fields_dict.section_angehoerige_links.is_collapsed()) {
		cur_frm.fields_dict.section_angehoerige_links.collapse();
	}
	if (cur_frm.fields_dict.section_rsv && !cur_frm.fields_dict.section_rsv.is_collapsed()) {
		cur_frm.fields_dict.section_rsv.collapse();
	}
	if (cur_frm.fields_dict.section_typ && !cur_frm.fields_dict.section_typ.is_collapsed()) {
		cur_frm.fields_dict.section_typ.collapse();
	}
	if (cur_frm.fields_dict.section_zeiterfassung && !cur_frm.fields_dict.section_zeiterfassung.is_collapsed()) {
		cur_frm.fields_dict.section_zeiterfassung.collapse();
	}
	
	cur_frm.fields_dict.section_person.collapse_link.on("click", function(){
		cur_frm.fields_dict.section_patienten_links.collapse();
	});
	cur_frm.fields_dict.section_patienten_links.collapse_link.on("click", function(){
		cur_frm.fields_dict.section_person.collapse();
	});
	if (cur_frm.fields_dict.section_kontakt_daten) {
		cur_frm.fields_dict.section_kontakt_daten.collapse_link.on("click", function(){
			cur_frm.fields_dict.section_rsv.collapse();
		});
		cur_frm.fields_dict.section_rsv.collapse_link.on("click", function(){
			cur_frm.fields_dict.section_kontakt_daten.collapse();
		});
	}
	if (cur_frm.fields_dict.section_angehoerige) {
		cur_frm.fields_dict.section_angehoerige.collapse_link.on("click", function(){
			cur_frm.fields_dict.section_angehoerige_links.collapse();
		});
		cur_frm.fields_dict.section_angehoerige_links.collapse_link.on("click", function(){
			cur_frm.fields_dict.section_angehoerige.collapse();
		});
	}
}

function fetch_rsv(frm) {
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
				cur_frm.set_df_property('rsv_kontaktdaten','options', r.message);
			}
		});
	}
}