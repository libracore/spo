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
			cur_frm.save();
			// open typ section
			setTimeout(function(){ cur_frm.fields[5].collapse_link.click(); }, 1000);
		}
	},
	refresh: function(frm) {
		//load dashboard
		if (frm.doc.anfrage_typ == 'Sonstiges') {
			update_dashboard(frm);
		}
		
		// timer action icon
		cur_frm.page.add_action_icon(__("fa fa-history"), function() {
			timesheet_handling(frm);
		});
		//add btn to create Mandat
		if (cur_frm.doc.mitglied) {
			frappe.call({
				method:"frappe.client.get_list",
				args:{
					doctype:"Anfrage",
					filters: [
						["mitglied","=", cur_frm.doc.mitglied]
					],
					fields: ["name"],
					order_by: 'creation'
				},
				callback: function(r) {
					if (r.message.length > 0) {
						if (r.message[(r.message.length - 1)].name == frm.doc.name) {
							frm.add_custom_button(__("Mandat"), function() {
								new_mandat(frm.doc.name, frm.doc.mitglied);
							});
						}
					}
				}
			});
		} else {
			frm.add_custom_button(__("Mandat"), function() {
				new_mandat(frm.doc.name, frm.doc.mitglied);
			});
		}
		
		//Set filter to mitgliedschaft
		cur_frm.fields_dict['mitgliedschaft'].get_query = function(doc) {
			 return {
				 filters: {
					 "mitglied": frm.doc.mitglied
				 }
			 }
		}
		
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
		
		//überprüfung ob kontakt- und adress-daten mit stamm übereinstimmen
		check_anfrage_daten_vs_stamm_daten(frm);
		
		//*******************************************************************************************
		// Diese Funktion muss in jedes SPO Beratungs-/Mandatspezifisches Dokument adaptiert werden!
		//*******************************************************************************************
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
						console.log($(this).attr("data-referenz"));
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
	import_mitgliederdaten: function(frm) {
		_import_mitgliederdaten(frm);
	},
	mitglied: function(frm) {
		_import_mitgliederdaten(frm);
		if (cur_frm.doc.mitglied) {
			frappe.call({
				method:"frappe.client.get_list",
				args:{
					doctype:"Anfrage",
					filters: [
						["mitglied","=", cur_frm.doc.mitglied]
					],
					fields: ["name"],
					order_by: 'creation'
				},
				callback: function(r) {
					if (r.message.length > 0) {
						if (r.message[(r.message.length - 1)].name == frm.doc.name) {
							frm.add_custom_button(__("Mandat"), function() {
								new_mandat(frm.doc.name, frm.doc.mitglied);
							});
						} else {
							cur_frm.remove_custom_button("Mandat");
						}
					}
				}
			});
		} else {
			frm.add_custom_button(__("Mandat"), function() {
				new_mandat(frm.doc.name, frm.doc.mitglied);
			});
		}
		cur_frm.scroll_to_field("mitgliedschaft");
	},
	mitglied_erstellen: function(frm) {
		frappe.call({
			method:"frappe.core.doctype.user.user.get_roles",
			args: {"uid":frappe.user.name}
		}).done((r)=>{
			var i;
			var has_role = false;
			for (i=0; i < r.message.length; i++) {
				if (r.message[i] == "Kundenstamm Verwaltung") {
					has_role = true;
				}
			}
			if (has_role) {
				//kontrolle ob pflichtfelder ausgefüllt
				var fehlende_daten = '';
				var fehler = false;
				if(!frm.doc.vorname) {
					fehlende_daten += 'Vorname<br>';
					fehler = true;
				}
				if(!frm.doc.nachname) {
					fehlende_daten += 'Nachname<br>';
					fehler = true;
				}
				if(!frm.doc.strasse) {
					fehlende_daten += 'Strasse<br>';
					fehler = true;
				}
				if(!frm.doc.plz) {
					fehlende_daten += 'Postleitzahl<br>';
					fehler = true;
				}
				
				var email = ''
				if (frm.doc.email) {
					if (frm.doc.email.split("@").length == 2) {
						if (frm.doc.email.split("@")[1].split(".").length == 2) {
							if (frm.doc.email.split("@")[1].split(".")[1] != '') {
								email = frm.doc.email;
							}
						}
					}
				}
				if (fehler) {
					frappe.msgprint("Bitte tragen Sie mindestens noch folgende Daten ein:<br>" + fehlende_daten, "Fehlende Daten");
				} else {
					frappe.call({
						"method": "spo.spo.doctype.anfrage.anfrage.create_new_mitglied",
						"args": {
							"vorname": frm.doc.vorname,
							"nachname": frm.doc.nachname,
							"strasse": frm.doc.strasse,
							"hausnummer": frm.doc.hausnummer,
							"ort": frm.doc.ort,
							"plz": frm.doc.plz,
							"email": email,
							"telefon": frm.doc.telefon,
							"mobile": frm.doc.mobile,
							"geburtsdatum": frm.doc.geburtsdatum,
							"kanton": frm.doc.kanton
						},
						"async": false,
						"callback": function(r) {
							if (r.message) {
								cur_frm.set_value('mitglied', r.message);
								cur_frm.save();
								frappe.msgprint("Das Mitglied <b>" + r.message + "</b> wurde angelegt<br><br>Bitte erfassen Sie noch die entsprechende Mitgliedschaft.", "Mitglied wurde angelegt");
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
	plz: function(frm) {
		get_city_from_pincode(cur_frm.doc.plz, 'ort', 'kanton');
	}
});

function new_mandat(anfrage, mitglied) {
	frappe.call({
		method: 'spo.spo.doctype.anfrage.anfrage.creat_new_mandat',
		args: {
			'anfrage': anfrage,
			'mitglied': mitglied
		},
		callback: function(r) {
			if(r.message) {
				if (r.message != 'already exist') {
					frappe.set_route("Form", "Mandat", r.message)
				} else {
					frappe.confirm(
						'Zu dieser Anfrage wurde bereits ein Mandat eröffnet.<br><br>Soll das/die Mandat(e) angezeigt werden?',
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
}

function show_mandat_list_based_on_anfrage() {
	frappe.route_options = {"anfragen": ["like", "%" + cur_frm.doc.name + "%"]};
	frappe.set_route("List", "Mandat");
}

function get_data_from_mitgliedernummer(frm, mitgliedernummer, inkl) {
	// Get Daten aus Kundenstamm
	frappe.call({
        "method": "frappe.client.get",
        "args": {
            "doctype": "Customer",
            "name": mitgliedernummer
        },
        "async": false,
        "callback": function(response) {
            var customer = response.message;
            cur_frm.set_value('vorname', customer.customer_name.split(" ")[0]);
			cur_frm.set_value('nachname', customer.customer_name.split(" ")[1]);
			cur_frm.set_value('mitglied', mitgliedernummer);
			
			// Get daten aus adresse
			frappe.call({
				"method": "spo.spo.doctype.anfrage.anfrage.get_address",
				"args": {
					"customer": customer.name
				},
				"async": false,
				"callback": function(r) {
					if(r.message) {
						frappe.call({
							"method": "frappe.client.get",
							"args": {
								"doctype": "Address",
								"name": r.message.name
							},
							"async": false,
							"callback": function(resp) {
								if(resp.message) {
									var address = resp.message;
									cur_frm.set_value('strasse', address.address_line1.split(" ")[0]);
									cur_frm.set_value('hausnummer', address.address_line1.split(" ")[1]);
									cur_frm.set_value('ort', address.city);
									cur_frm.set_value('plz', address.pincode);
								}
								if(inkl) {
									get_valid_mitgliedschaft_based_on_mitgliedernummer(frm, mitgliedernummer)
								}
								
								frappe.call({
									"method": "spo.spo.doctype.anfrage.anfrage.get_contact",
									"args": {
										"doctype": "Address",
										"customer": customer.name
									},
									"async": false,
									"callback": function(resp) {
										if(resp.message) {
											var contact = resp.message;
											cur_frm.set_value('telefon', contact.phone);
											cur_frm.set_value('mobile', contact.mobile_no);
											cur_frm.set_value('email', contact.email_id);
											cur_frm.set_value('geburtsdatum', contact.geburtsdatum);
										}
									}
								});
							}
						});
					} else {
						if(inkl) {
							get_valid_mitgliedschaft_based_on_mitgliedernummer(frm, mitgliedernummer)
						}
					}
				}
			});
			
			
			if(inkl) {
				get_valid_mitgliedschaft_based_on_mitgliedernummer(frm, mitgliedernummer)
			}
        }
    });
}

function get_data_from_mitgliedschaft(frm, mitgliedschaft) {
	cur_frm.set_value('mitgliedschaft', mitgliedschaft);
	frappe.call({
        "method": "frappe.client.get",
        "args": {
            "doctype": "Mitgliedschaft",
            "name": mitgliedschaft
        },
        "async": false,
        "callback": function(response) {
            var mitgliedschaft = response.message;
			get_data_from_mitgliedernummer(frm, mitgliedschaft.mitglied, false);
        }
    });
}

function get_valid_mitgliedschaft_based_on_mitgliedernummer(frm, mitgliedernummer) {
	frappe.call({
        "method": "spo.spo.doctype.anfrage.anfrage.get_valid_mitgliedschaft_based_on_mitgliedernummer",
        "args": {
            "mitgliedernummer": mitgliedernummer
        },
        "async": false,
        "callback": function(r) {
            if (r.message.length >= 1) {
				cur_frm.set_value('mitgliedschaft', r.message[0].name);
				if (r.message.length > 1) {
					frappe.msgprint("<b>Achtung!</b><br>Das Mitglied besitzt mehere gültige Mitgliedschaften, bitte prüfen Sie die autom. Selektion!", "Mehere gültige Mitgliedschaft");
				}
			} else {
				frappe.msgprint("<b>Achtung!</b><br>Das Mitglied besitzt keine gültige Mitgliedschaft!", "Keine gültige Mitgliedschaft");
			}
        }
    });
}

function get_vorschlagswerte(frm) {
	frappe.call({
        "method": "spo.spo.doctype.anfrage.anfrage.get_vorschlagswerte",
        "args": {
            "vorname": frm.doc.vorname,
			"nachname": frm.doc.nachname,
			"strasse": frm.doc.strasse,
			"hausnummer": frm.doc.hausnummer,
			"ort": frm.doc.ort,
			"plz": frm.doc.plz,
			"frm": frm.doc.name,
			"geburtsdatum": frm.doc.geburtsdatum
        },
        "async": false,
        "callback": function(response) {
            var vorschlagswerte = "Keine Daten gefunden";
			if (response) {
				var vorschlagswerte = response.message;
			}
			frappe.msgprint(vorschlagswerte.full_matches + "<hr>" + vorschlagswerte.namens_matches + "<hr>" + vorschlagswerte.address_matches, 'Suchresultate');
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
					frappe.msgprint("Die hinterlegte Mitgliedschaft ist abgelaufen!", 'Achtung');
				}
			}
		});
	}
}

function update_dashboard(frm) {
	frappe.call({
		"method": "spo.spo.doctype.anfrage.anfrage.get_dashboard_data",
		"args": {
			"mitglied": frm.doc.mitglied,
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
				labels: ["Verwendet", "Ausstehend"],

				datasets: [
					{
						values: [query.callcenter_verwendet, query.callcenter_limit - query.callcenter_verwendet]
					}
				],

				},
				title: "Zeitauswertung (in min)",
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
		cur_frm.set_df_property('kanton','reqd', 1);
		cur_frm.set_df_property('problematik','reqd', 1);
		if (frm.doc.anfrage_typ == 'Hotline') {
			cur_frm.set_value('kontakt_via', 'Telefon');
			cur_frm.set_df_property('kontakt_via','read_only', 1);
			cur_frm.set_df_property('vorname','reqd', 0);
			cur_frm.set_df_property('nachname','reqd', 0);
			cur_frm.set_df_property('geburtsdatum','reqd', 0);
			cur_frm.set_df_property('kanton','reqd', 0);
			cur_frm.set_df_property('strasse','reqd', 0);
			cur_frm.set_df_property('hausnummer','reqd', 0);
			cur_frm.set_df_property('ort','reqd', 0);
			cur_frm.set_df_property('plz','reqd', 0);
			cur_frm.set_df_property('email','reqd', 0);
			if (frm.doc.anonymisiert == 1) {
				cur_frm.set_df_property('kanton','reqd', 1);
				cur_frm.set_df_property('nachname','reqd', 0);
			} else {
				cur_frm.set_df_property('kanton','reqd', 1);
				cur_frm.set_df_property('nachname','reqd', 1);
			}
		} else {
			cur_frm.set_df_property('kontakt_via','read_only', 0);
			cur_frm.set_df_property('vorname','reqd', 1);
			cur_frm.set_df_property('nachname','reqd', 1);
			cur_frm.set_df_property('geburtsdatum','reqd', 1);
			cur_frm.set_df_property('kanton','reqd', 1);
			cur_frm.set_df_property('strasse','reqd', 1);
			cur_frm.set_df_property('hausnummer','reqd', 1);
			cur_frm.set_df_property('ort','reqd', 1);
			cur_frm.set_df_property('plz','reqd', 1);
			cur_frm.set_df_property('email','reqd', 1);
			cur_frm.set_df_property('spo_ombudsstelle','reqd', 1);
			cur_frm.set_df_property('kontakt_via','reqd', 1);
		}
		if (cur_frm.doc.problematik == 'Krankenkasse (Grundversicherung)') {
			cur_frm.set_df_property('krankenkasse','reqd', 1);
		}
	}
}

function check_anfrage_daten_vs_stamm_daten(frm) {
	var i;
	var assign = true;
	if (cur_frm.get_docinfo().assignments) {
		for (i=0; i < cur_frm.get_docinfo().assignments.length; i++) {
			if (cur_frm.get_docinfo().assignments[i].description.includes("Bitte folgende Änderungen in den Stammdaten vornehmen:")) {
				assign = false;
			}
		}
	}
	if (frm.doc.mitglied && assign) {
		frappe.call({
			"method": "spo.spo.doctype.anfrage.anfrage.check_anfrage_daten_vs_stamm_daten",
			"args": {
				"mitglied": frm.doc.mitglied,
				"vorname": frm.doc.vorname || '',
				"nachname": frm.doc.nachname || '',
				"geburtsdatum": frm.doc.geburtsdatum || '',
				"kanton": frm.doc.kanton || '',
				"strasse": frm.doc.strasse || '',
				"hausnummer": frm.doc.hausnummer || '',
				"ort": frm.doc.ort || '',
				"plz": frm.doc.plz || '',
				"telefon": frm.doc.telefon || '',
				"mobile": frm.doc.mobile || '',
				"email": frm.doc.email || ''
			},
			"callback": function(response) {
				var abweichungen = response.message.abweichungen;
				var assign_to = response.message.assign_to;
				if (abweichungen != '') {
					frappe.confirm(
						'<p>Sollen folgende Änderungen der zuständigen Abteilung zur Verarbeitung übergeben werden?</p>' + abweichungen,
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
				"description": "Bitte folgende Änderungen in den Stammdaten vornehmen:<br>" + abweichungen
			},
			"callback": function(response) {
				frappe.msgprint("Die Stammdaten Änderung wurde zugewiesen.", "Zuweisung erfolgreich");
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
				"description": "Bitte Kundenstamm anlegen."
			},
			"callback": function(response) {
				frappe.msgprint("Die Stammdaten Anlage wurde zugewiesen.", "Zuweisung erfolgreich");
				cur_frm.reload_doc();
			}
		});
	}
}

function _import_mitgliederdaten(frm) {
	if (frm.doc.mitglied) {
		// laden aller Daten aus Mitgliedernummer
		if(frm.doc.mitgliedschaft) {
			get_data_from_mitgliedernummer(frm, frm.doc.mitglied, false);
		} else {
			get_data_from_mitgliedernummer(frm, frm.doc.mitglied, true);
		}
	} else if(frm.doc.mitgliedschaft) {
		// laden aller Daten aus Mitgliedschaft
		get_data_from_mitgliedschaft(frm, frm.doc.mitgliedschaft);
	} else {
		frappe.prompt([
			{'fieldname': 'mitgliedernummer', 'fieldtype': 'Link', 'label': 'Mitgliedernummer', 'reqd': 0, 'options': 'Customer'},
			{'fieldname': 'mitgliedschaft', 'fieldtype': 'Link', 'label': 'Mitgliedschaft', 'reqd': 0, 'options': 'Mitgliedschaft'},
			{'fieldname': 'txt', 'fieldtype': 'HTML', 'label': 'Beschreibung', 'reqd': 0, 'options': '<p>Wenn Ihnen eine Mitglieder- und/oder Mitgliedschaftsnummer bekannt ist, können Sie diese hier zur Suchoptimierung eintragen. Haben Sie keine der genannten Angaben, können Sie die Felder leer lassen.</p>'}
		],
		function(values){
			var mitgliedernummer = '';
			if (values.mitgliedernummer) {
				mitgliedernummer = values.mitgliedernummer;
			}
			var mitgliedschaft = '';
			if (values.mitgliedschaft) {
				mitgliedschaft = values.mitgliedschaft;
			}
			if (mitgliedernummer) {
				// laden aller Daten aus Mitgliedernummer
				if(mitgliedschaft) {
					get_data_from_mitgliedernummer(frm, mitgliedernummer, false);
				} else {
					get_data_from_mitgliedernummer(frm, mitgliedernummer, true);
				}
				
				// setzen der Mitgliedernummer in der Anfrage
				cur_frm.set_value('mitglied', values.mitgliedernummer);
			} else if (mitgliedschaft) {
				// laden aller Daten aus Mitgliedschaft
				get_data_from_mitgliedschaft(frm, mitgliedschaft);
				
				// setzen der Mitgliedschaft in der Anfrage
				cur_frm.set_value('mitgliedschaft', values.mitgliedschaft);
			} else {
				// laden Vorschlagsdaten...
				get_vorschlagswerte(frm);
			}
		},
		'Haben Sie eine Mitglieder- oder Mitgliedschaftsnummer?<br>Wenn nicht, können Sie die Felder leer lassen um zu suchen.',
		'Daten importieren'
		);
	}
}

function timesheet_handling(frm) {
	frappe.prompt([
		{'fieldname': 'time', 'fieldtype': 'Float', 'label': 'Arbeitszeit (in h)', 'reqd': 1}  
	],
	function(values){
		frappe.call({
			"method": "spo.utils.timesheet_handlings.handle_timesheet",
			"args": {
				"user": frappe.session.user_email,
				"doctype": frm.doc.doctype,
				"reference": frm.doc.name,
				"time": values.time
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

//*******************************************************************************************
// Diese Funktion muss in jedes SPO Beratungs-/Mandatspezifisches Dokument adaptiert werden!
//*******************************************************************************************
function ts_bearbeiten(ts) {
	frappe.route_options = {"timesheet": ts};
	frappe.set_route("Form", "Zeiterfassung");
}