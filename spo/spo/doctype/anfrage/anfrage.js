// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

// mitgliedschaft = Mitgliedschaft (Typ, Von, Bis)
// mitglied = Kunde
// mitgliedernummer = Kundennummer

frappe.ui.form.on('Anfrage', {
	onload: function(frm) {
		if (frm.doc.__islocal) {
			start_timer(frm);
			cur_frm.save();
		}
	},
	refresh: function(frm) {
		//add btn to create Mandat
		frappe.call({
			method:"frappe.client.get_list",
			args:{
				doctype:"Anfrage",
				filters: [
					["mitglied","=", frm.doc.mitglied]
				],
				fields: ["name"],
				order_by: 'creation'
			},
			callback: function(r) {
				if (r.message[(r.message.length - 1)].name == frm.doc.name) {
					frm.add_custom_button(__("Convert to/Open Mandat"), function() {
						new_mandat(frm.doc.name, frm.doc.mitglied);
					});
				}
			}
		});
		
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
		
		//erstellen des Dashboards, wenn ein Mitglied eingetragen ist
		if (frm.doc.mitglied) {
			if (frm.doc.anfrage_typ == 'Sonstiges') {
				update_dashboard(frm);
			}
		}
		
		//show/hide timer stop btn
		if (frm.doc.timer_status == 1) {
			frm.add_custom_button(__("Stop Timer"), function() {
				stop_timer(frm);
			}).addClass("btn-primary");
		} else {
			frm.add_custom_button(__("Start Timer"), function() {
				start_timer(frm);
			}).addClass("btn-primary");
		}
		
		// add scroll to navbar
		add_scroll_to(frm);
	},
	import_mitgliederdaten: function(frm) {
		if (frm.doc.mitglied) {
			// laden aller Daten aus Mitgliedernummer
			if(frm.doc.mitgliedschaft) {
				get_data_from_mitgliedernummer(frm, frm.doc.mitglied, false);
			} else {
				get_data_from_mitgliedernummer(frm, frm.doc.mitglied, true);
			}
			console.log("Lade Daten von " + frm.doc.mitglied);
		} else if(frm.doc.mitgliedschaft) {
			// laden aller Daten aus Mitgliedschaft
			get_data_from_mitgliedschaft(frm, frm.doc.mitgliedschaft);
			console.log("Lade Daten von " + frm.doc.mitgliedschaft);
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
					console.log("Lade Daten von " + mitgliedernummer);
					if(mitgliedschaft) {
						get_data_from_mitgliedernummer(frm, mitgliedernummer, false);
					} else {
						get_data_from_mitgliedernummer(frm, mitgliedernummer, true);
					}
					
					// setzen der Mitgliedernummer in der Anfrage
					cur_frm.set_value('mitglied', values.mitgliedernummer);
				} else if (mitgliedschaft) {
					// laden aller Daten aus Mitgliedschaft
					console.log("Lade Daten von " + mitgliedschaft);
					get_data_from_mitgliedschaft(frm, mitgliedschaft);
					
					// setzen der Mitgliedschaft in der Anfrage
					cur_frm.set_value('mitgliedschaft', values.mitgliedschaft);
				} else {
					// laden Vorschlagsdaten...
					console.log("laden Vorschlagsdaten...");
					get_vorschlagswerte(frm);
				}
			},
			'Haben Sie eine Mitglieder- oder Mitgliedschaftsnummer?<br>Wenn nicht, können Sie die Felder leer lassen um zu suchen.',
			'Daten importieren'
			);
		}
	},
	mitglied_erstellen: function(frm) {
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
					"email": frm.doc.email,
					"telefon": frm.doc.telefon,
					"mobile": frm.doc.mobile
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
	},
	manuelle_korrektur: function(frm) {
		cur_frm.set_df_property('timer','read_only',0);
	},
	scroll_top_0: function(frm) {
		frappe.utils.scroll_to(0);
		var sections = document.getElementsByClassName("row form-section visible-section");
		sections[2].childNodes[0].childNodes[0].click();
	},
	scroll_top_1: function(frm) {
		frappe.utils.scroll_to(0);
		var sections = document.getElementsByClassName("row form-section visible-section");
		sections[3].childNodes[0].childNodes[0].click();
	},
	scroll_top_2: function(frm) {
		frappe.utils.scroll_to(0);
		var sections = document.getElementsByClassName("row form-section visible-section");
		sections[4].childNodes[0].childNodes[0].click();
	},
	scroll_top_3: function(frm) {
		frappe.utils.scroll_to(0);
		var sections = document.getElementsByClassName("row form-section visible-section");
		sections[5].childNodes[0].childNodes[0].click();
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
									cur_frm.set_value('telefon', address.phone);
									cur_frm.set_value('mobile', address.fax);
									cur_frm.set_value('email', address.email_id);
								}
								if(inkl) {
									get_valid_mitgliedschaft_based_on_mitgliedernummer(frm, mitgliedernummer)
								}
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
			"frm": frm.doc.name
        },
        "async": false,
        "callback": function(response) {
            var vorschlagswerte = "Keine Daten gefunden";
			if (response) {
				var vorschlagswerte = response.message;
			}
			console.log(vorschlagswerte);
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

function start_timer(frm) {
	cur_frm.set_value('timer_start', frappe.datetime.now_datetime());
	cur_frm.set_value('timer_status', 1);
	cur_frm.save();
}

function stop_timer(frm) {
	cur_frm.set_value('timer_status', 0);
	frappe.call({
		"method": "spo.spo.doctype.anfrage.anfrage.get_timer_diff",
		"args": {
			"start": frm.doc.timer_start,
			"ende": frappe.datetime.now_datetime()
		},
		"async": false,
		"callback": function(response) {
			console.log(Math.round(response.message));
			cur_frm.set_value('timer', cur_frm.doc.timer + Math.round(response.message));
			cur_frm.save();
		}
	});
}

function update_dashboard(frm) {
	frappe.call({
		"method": "spo.spo.doctype.anfrage.anfrage.get_dashboard_data",
		"args": {
			"mitglied": frm.doc.mitglied,
			"anfrage": frm.doc.name
		},
		"async": false,
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
			
			check_mitgliedschafts_unterbruch(frm, query.mitgliedschaften, query.limite_unterbruch);
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

function add_scroll_to(frm) {
	//get referenzpunkte und create grundgerüst
	var vorhandene_sidebar = document.getElementsByClassName("list-unstyled sidebar-menu")[3];
	var sections = document.getElementsByClassName("row form-section visible-section");
	
	var ul = document.createElement("ul");
	ul.classList.add("list-unstyled");
	ul.classList.add("sidebar-menu");
	
	var li1 = document.createElement("li");
	li1.classList.add("divider");
	
	var li2 = document.createElement("li");
	li2.style.position = "relative";
	
	var li3 = document.createElement("li");
	li3.classList.add("h6");
	li3.classList.add("attachments-label");
	var li3_node = document.createTextNode("Scroll to...");
	li3.appendChild(li3_node);
	
	// link zu "Anfragen Typisierung"
	var a0 = document.createElement("a");
	a0.classList.add("sidebar-comments");
	a0.classList.add("badge-hover");
	a0.onclick = function(){frappe.utils.scroll_to(sections[2], !0); sections[2].childNodes[0].childNodes[0].click();};
	
	var span0 = document.createElement("span")
	var span_node0 = document.createTextNode("Anfragen Typisierung");
	
	// link zu "Angaben zur Person"
	var a1 = document.createElement("a");
	a1.classList.add("sidebar-comments");
	a1.classList.add("badge-hover");
	a1.onclick = function(){frappe.utils.scroll_to(sections[3], !0); sections[3].childNodes[0].childNodes[0].click();};
	
	var span1 = document.createElement("span")
	var span_node1 = document.createTextNode("Angaben zur Person");
	
	// link zu "Angaben zur Anfrage"
	var a2 = document.createElement("a");
	a2.classList.add("sidebar-comments");
	a2.classList.add("badge-hover");
	a2.onclick = function(){frappe.utils.scroll_to(sections[4], !0); sections[4].childNodes[0].childNodes[0].click();};
	
	var span2 = document.createElement("span")
	var span_node2 = document.createTextNode("Angaben zur Anfrage");
	
	// link zu "Zeiterfassung"
	var a3 = document.createElement("a");
	a3.classList.add("sidebar-comments");
	a3.classList.add("badge-hover");
	a3.onclick = function(){frappe.utils.scroll_to(sections[5], !0); sections[5].childNodes[0].childNodes[0].click();};
	
	var span3 = document.createElement("span")
	var span_node3 = document.createTextNode("Zeiterfassung");
	
	// verknüpfen "Anfragen Typisierung"
	span0.appendChild(span_node0);
	a0.appendChild(span0);
	li2.appendChild(a0);
	
	// verknüpfen "Angaben zur Person"
	span1.appendChild(span_node1);
	a1.appendChild(span1);
	li2.appendChild(a1);
	
	// verknüpfen "Angaben zur Anfrage"
	span2.appendChild(span_node2);
	a2.appendChild(span2);
	li2.appendChild(a2);
	
	// verknüpfen "Zeiterfassung"
	span3.appendChild(span_node3);
	a3.appendChild(span3);
	li2.appendChild(a3);
	
	// verknüpfen Grundgerüst
	ul.appendChild(li1);
	ul.appendChild(li3);
	ul.appendChild(li2);
	vorhandene_sidebar.parentElement.insertBefore(ul, vorhandene_sidebar);
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