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
		frm.add_custom_button(__("Convert to Mandat"), function() {
            new_mandat(frm.doc.name);
        });
		
		//Set filter to mitgliedschaft
		cur_frm.fields_dict['mitgliedschaft'].get_query = function(doc) {
			 return {
				 filters: {
					 "mitglied": frm.doc.mitglied
				 }
			 }
		}
		
		//prüfen ob Mitgliedschaft gültig ist, wenn eine Mitgliedschaft eingetragen ist
		if (frm.doc.mitgliedschaft) {
			check_mitgliedschaft_ablaufdatum(frm);
		}
		
		//erstellen des Dashboards, wenn ein Mitglied eingetragen ist
		if (frm.doc.mitglied) {
			update_dashboard(frm);
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
			'Haben Sie eine Mitglieder- oder Mitgliedschaftsnummer?',
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
	}
});

function new_mandat(anfrage) {
	frappe.call({
		method: 'spo.scripts.mandat.creat_new_mandat',
		args: {
			'anfrage': anfrage
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
			"mitglied": frm.doc.mitglied
		},
		"async": false,
		"callback": function(response) {
			var query = response.message;
			let chart = new Chart( "#chart", { // or DOM element
				data: {
				labels: ["Letztes Jahr", "YTD", "Q1", "Q2", "Q3", "Q4"],

				datasets: [
					{
						name: "Als Mitglied", chartType: 'bar',
						values: [query.m_last_year, query.m_ytd, query.m_q1, query.m_q2, query.m_q3, query.m_q4]
					},
					{
						name: "Ohne<br>Mitgliedschaft", chartType: 'bar',
						values: [query.o_last_year, query.o_ytd, query.o_q1, query.o_q2, query.o_q3, query.o_q4]
					},
					{
						name: "&Oslash;", chartType: 'line',
						values: [(query.m_last_year + query.o_last_year) / 2, (query.m_ytd + query.o_ytd) / 2, (query.m_q1 + query.o_q1) / 2, (query.m_q2 + query.o_q2) / 2, (query.m_q3 + query.o_q3) / 2, (query.m_q4 + query.o_q4) / 2]
					},
					{
						name: "Total", chartType: 'line',
						values: [(query.m_last_year + query.o_last_year), (query.m_ytd + query.o_ytd), (query.m_q1 + query.o_q1), (query.m_q2 + query.o_q2), (query.m_q3 + query.o_q3), (query.m_q4 + query.o_q4)]
					}
				],

				yMarkers: [{ label: "Mittelwert", value: (query.m_last_year + query.o_last_year + query.m_ytd + query.o_ytd + query.m_q1 + query.o_q1 + query.m_q2 + query.o_q2 + query.m_q3 + query.o_q3 + query.m_q4 + query.o_q4) / 12,
					options: { labelPos: 'left' }}],
				/*yRegions: [{ label: "Region", start: -10, end: 50,
					options: { labelPos: 'right' }}]
				*/},

				title: "Dashboard",
				type: 'axis-mixed', // or 'bar', 'line', 'pie', 'percentage'
				height: 180,
				colors: ['#00b000', '#d40000', 'light-blue', 'blue'],

				tooltipOptions: {
					formatTooltipX: d => (d + '').toUpperCase(),
					formatTooltipY: d => d + ' min',
				}
			});
		}
	});
}