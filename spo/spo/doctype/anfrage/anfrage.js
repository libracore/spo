// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

// mitgliedschaft = Mitgliedschaft (Typ, Von, Bis)
// mitglied = Kunde
// mitgliedernummer = Kundennummer

frappe.ui.form.on('Anfrage', {
	setup: function(frm) {
		if (frm.doc.__islocal) {
			cur_frm.save();
		}
	},
	refresh: function(frm) {
		//add btn to create Mandat
		frm.add_custom_button(__("Convert to Mandat"), function() {
            new_mandat(frm.doc.name);
        });
		//var import_mitgliederdaten_btn = frm.fields_dict.import_mitgliederdaten.input //.addEventListener("click", function(frm) { console.log("yess duuuu"); } );
		//console.log(import_mitgliederdaten_btn);
		//import_mitgliederdaten_btn.addEventListener("click", function(frm) { console.log("yess duuuu"); } );
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
		frappe.msgprint("Muss noch programmiert werden....");
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
			get_data_from_mitgliedernummer(frm, mitgliedschaft.customer, false);
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