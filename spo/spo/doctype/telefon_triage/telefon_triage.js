// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Telefon Triage', {
	refresh: function(frm) {
		cur_frm.disable_save();
		show_mitglied_in_html(frm);
	},
	reset_suche: function(frm) {
		show_mitglied_suche_in_html(frm);
		cur_frm.set_value('vorname', '');
		cur_frm.set_value('nachname', '');
		cur_frm.set_value('geburtsdatum', '');
		cur_frm.set_value('strasse', '');
		cur_frm.set_value('plz', '');
		cur_frm.set_value('ort', '');
		cur_frm.set_value('kanton', '');
		cur_frm.set_value('kunde', '');
		cur_frm.set_value('kontakt', '');
		cur_frm.set_value('adresse', '');
		cur_frm.set_value('mitgliedschaft', '');
	},
	suchen: function(frm) {
		kontaktdaten_suchen(frm);
	},
	open_anfrage: function(frm) {
		frappe.msgprint("Dies muss noch programmiert werden...");
	}
});

function show_mitglied_suche_in_html(frm) {
	cur_frm.set_df_property('info_html','options', '<div class="alert alert-info"><strong>Bitte suchen Sie nach einem möglichen Mitglied.</strong></div>');
}

function show_mitglied_in_html(frm) {
	cur_frm.set_df_property('info_html','options', '<div class="alert alert-success"><strong>Mitglied gefunden: </strong>Die gesuchten Daten entsprechen einem gültigen Mitglied.<br>Sie können eine Anfrage eröffnen.</div>');
}

function show_nicht_mitglied_in_html(frm) {
	cur_frm.set_df_property('info_html','options', '<div class="alert alert-danger"><strong>Achtung: </strong>Die gesuchten Daten entsprechen <b>keinem gültigen Mitglied</b>!<br>Dient die SPO als Ombudstelle? Wenn ja können eine Anfrage eröffnen, ansonsten bitte an die Hotline verweisen.</div>');
}

function kontaktdaten_suchen(frm) {
	var vorname = cur_frm.doc.vorname;
	var nachname = cur_frm.doc.nachname;
	var strasse = cur_frm.doc.strasse;
	var plz = cur_frm.doc.plz;
	var ort = cur_frm.doc.ort;
	var kanton = cur_frm.doc.kanton;
	var geburtsdatum = cur_frm.doc.geburtsdatum;
	
	frappe.call({
		"method": "spo.spo.doctype.anfrage.anfrage.kontaktdaten_suchen",
		"args": {
			'vorname': vorname,
			'nachname': nachname,
			'strasse': strasse,
			'plz': plz,
			'ort': ort,
			'kanton': kanton,
			'geburtsdatum': geburtsdatum
		},
		"callback": function(r) {
			if (r.message) {
				var full_matches = r.message.full_matches;
				var alle_kontakte = r.message.alle_kontakte;
				var alle_adressen = r.message.alle_adressen;
				
				var d = new frappe.ui.Dialog({
					'fields': [
						{'fieldname': 'header_1', 'fieldtype': 'Heading', 'label': 'Vollständige Treffer'},
						{'fieldname': 'full_matches', 'fieldtype': 'HTML', 'options': '<div><p>Keine vollständige Treffer</p></div>'},
						{'fieldname': 'header_2', 'fieldtype': 'Heading', 'label': 'Zutreffende Kontakte'},
						{'fieldname': 'alle_kontakte', 'fieldtype': 'HTML', 'options': '<div><p>Keine zutreffende Kontakte</p></div>'},
						{'fieldname': 'header_3', 'fieldtype': 'Heading', 'label': 'Zutreffende Adressen'},
						{'fieldname': 'alle_adressen', 'fieldtype': 'HTML', 'options': '<div><p>Keine zutreffende Adressen</p></div>'}
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
			cur_frm.set_value('kunde', $(all_radios[i]).data('customer'));
			check_mitgliedschaft(frm);
			if ($(all_radios[i]).data('match') == 'full') {
				cur_frm.set_value('adresse', $(all_radios[i]).data('adresse'));
				cur_frm.set_value('kontakt', $(all_radios[i]).data('kontakt'));
				
				frappe.db.get_value('Address', {'name': cur_frm.doc.adresse}, ['address_line1', 'plz', 'city', 'kanton'], (r) => {
					cur_frm.set_value('strasse', r.address_line1);
					cur_frm.set_value('ort', r.city);
					cur_frm.set_value('kanton', r.kanton);
					cur_frm.set_value('plz', r.plz);
				});
				
				frappe.db.get_value('Contact', {'name': cur_frm.doc.kontakt}, ['first_name', 'last_name', 'geburtsdatum'], (r) => {
					cur_frm.set_value('vorname', r.first_name);
					cur_frm.set_value('nachname', r.last_name);
					cur_frm.set_value('geburtsdatum', r.geburtsdatum);
				});
			} else if ($(all_radios[i]).data('match') == 'adresse') {
				cur_frm.set_value('adresse', $(all_radios[i]).data('adresse'));
				
				frappe.db.get_value('Address', {'name': cur_frm.doc.adresse}, ['address_line1', 'plz', 'city', 'kanton'], (r) => {
					cur_frm.set_value('strasse', r.address_line1);
					cur_frm.set_value('ort', r.city);
					cur_frm.set_value('kanton', r.kanton);
					cur_frm.set_value('plz', r.plz);
				});
			} else if ($(all_radios[i]).data('match') == 'kontakt') {
				cur_frm.set_value('kontakt', $(all_radios[i]).data('kontakt'));
				
				frappe.db.get_value('Contact', {'name': cur_frm.doc.kontakt}, ['first_name', 'last_name', 'geburtsdatum'], (r) => {
					cur_frm.set_value('vorname', r.first_name);
					cur_frm.set_value('nachname', r.last_name);
					cur_frm.set_value('geburtsdatum', r.geburtsdatum);
				});
			}
		}
	}
	
	d.hide();
}

function check_mitgliedschaft(frm) {
	if (cur_frm.doc.kunde) {
		frappe.call({
			method:"frappe.client.get_list",
			args:{
				doctype:"Mitgliedschaft",
				filters: [
					["mitglied","=", cur_frm.doc.kunde],
					["ende",">=", frappe.datetime.get_today()]
				],
				fields: ["name"],
				order_by: 'ende'
			},
			callback: function(r) {
				if (r.message.length) {
					cur_frm.set_value('mitgliedschaft', r.message[0].name);
					show_mitglied_in_html(frm);
				} else {
					show_nicht_mitglied_in_html(frm);
					cur_frm.set_value('mitgliedschaft', '');
				}
			}
		});
	}
}