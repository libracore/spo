// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

var make_default_ts_entry = false;

frappe.ui.form.on('Anforderung Patientendossier', {
	refresh: function(frm) {
		// filter for textbaustein based on doctype and user
		cur_frm.fields_dict['textbaustein'].get_query = function(doc) {
			 return {
				 filters: {
					 "mitarbeiter": frappe.user.name,
					 "dokument": "Anforderung Patientendossier"
				 }
			 }
		}
		cur_frm.fields_dict['spital'].get_query = function(doc) {
			 return {
				 filters: {
					 "customer_group": "Spital",
					 "disabled": 0
				 }
			 }
		}
		cur_frm.fields_dict['spital_kontakt'].get_query = function(doc) {
			return {
				filters: {
					"link_doctype": "Customer",
					"link_name": frm.doc.spital
				}
			}
		};
		cur_frm.fields_dict['spital_adresse'].get_query = function(doc) {
			return {
				filters: {
					"link_doctype": "Customer",
					"link_name": frm.doc.spital
				}
			}
		};
		// timer action icon
		cur_frm.page.add_action_icon(__("fa fa-history"), function() {
			timesheet_handling(frm);
		});
		
		defaul_texte(frm);
		
		if (cur_frm.doc.mandat) {
			frm.add_custom_button(__("Zurück zum Mandat"), function() {
				frappe.set_route("Form", "Mandat", cur_frm.doc.mandat);
			});
		}
		
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
	},
	onload: function(frm) {
		defaul_texte(frm);
		set_kunden_html(frm);
		if (cur_frm.is_new()||!cur_frm.doc.titelzeile||cur_frm.doc.titelzeile == "<div><br></div>") {
			set_titelzeile(frm);
		}
		if (cur_frm.is_new()) {
			make_default_ts_entry = true;
		}
	},
	mahnstufe_1: function(frm) {
		defaul_texte(frm);
	},
	mahnstufe_2: function(frm) {
		defaul_texte(frm);
	},
	customer: function(frm) {
		set_kunden_html(frm);
		set_titelzeile(frm);
	},
	kunden_adresse: function(frm) {
		set_kunden_html(frm);
		set_titelzeile(frm);
	},
	kunden_kontakt: function(frm) {
		set_kunden_html(frm);
		set_titelzeile(frm);
	},
	spital: function(frm) {
		cur_frm.set_value("spital_kontakt", "");
		cur_frm.set_value("spital_adresse", "");
		if (cur_frm.doc.spital) {
			frappe.db.get_value('Customer', {'name': cur_frm.doc.spital}, ['customer_name', 'customer_type'], (r) => {
				if (r.customer_type == 'Company') {
					cur_frm.set_value("adressat", r.customer_name);
				}
			});
		}
	},
	spital_kontakt: function(frm) {
		if (cur_frm.doc.spital_kontakt) {
			frappe.db.get_value('Contact', {'name': cur_frm.doc.spital_kontakt}, ['salutation', 'first_name', 'last_name', 'designation'], (kontakt) => {
				var adresse = '';
				if (cur_frm.doc.adressat) {
					adresse = cur_frm.doc.adressat;
					adresse += '\n';
				}
				if (kontakt.salutation) {
					adresse += kontakt.salutation;
					adresse += '\n';
				}
				adresse += kontakt.first_name;
				adresse += ' ';
				adresse += kontakt.last_name;
				if (kontakt.designation) {
					adresse += '\n';
					adresse += kontakt.designation;
				}
				cur_frm.set_value("adressat", adresse);
			});
		}
	},
	spital_adresse: function(frm) {
		if (cur_frm.doc.spital_adresse) {
			frappe.db.get_value('Address', {'name': cur_frm.doc.spital_adresse}, ['address_line1', 'address_line2', 'plz', 'city', 'override_customer_name', 'new_address_heading'], (adressen_link) => {
				
                // special handling if override_customer_name in address
                if (adressen_link.override_customer_name == 1) {
                    frappe.db.get_value('Customer', {'name': cur_frm.doc.spital}, ['customer_name', 'customer_type'], (r) => {
                        if (r.customer_type == 'Company') {
                            cur_frm.set_value("adressat", cur_frm.doc.adressat.replace(r.customer_name, adressen_link.new_address_heading));
                        }
                    });
                }
                
                var adresse = '';
                if (cur_frm.doc.adressat) {
                    adresse = cur_frm.doc.adressat;
                    adresse += '\n';
                }
                adresse += adressen_link.address_line1;
                adresse += '\n';
                if (adressen_link.address_line2) {
                    adresse += adressen_link.address_line2;
                    adresse += '\n';
                }
                adresse += adressen_link.plz;
                adresse += ' ';
                adresse += adressen_link.city;
                cur_frm.set_value("adressat", adresse);
			});
		}
	}
});

function defaul_texte(frm) {
	if (!cur_frm.doc.textbaustein && (!cur_frm.doc.brieftext||cur_frm.doc.brieftext=="<div><br></div>")) {
		if (!cur_frm.doc.mahnstufe_1  && !cur_frm.doc.mahnstufe_2) {
			var brieftext_string = '<p><b>Herausgabe Patientendossier - betreffend Operation vom 22.09.2019, Femurkopfendoprothese links</b></p><br>' +
				'<p>Sehr geehrter Herr Dr. X</p><br>' +
				'<p>Frau yz wandte sich an die Stiftung SPO Patientenorganisation und bat uns, für sie folgende Unterlagen zu verlangen:</p><br>' +
				'<p><b>vollständiges Patientendossier seit 21.09.2019 mit:</b></p><br>' +
				'<ul><li>Untersuchungs- und Sprechstundenberichte</li>' +
				'<li>OP-Aufklärung</li>' +
				'<li>OP-Bericht</li>' +
				'<li>Arztverlaufsbericht, Austrittsbericht</li>' +
				'<li>Röntgenbefunde und Röntgenbilder auf Datenträger oder mit E-Zugangscode</li></ul><br>' +
				'<p>Wir danken Ihnen für die baldige Zusendung.</p><br>' +
				'<p>Freundliche Grüsse</p><br>' +
				'<p>Name Beraterin, Beratung</p><br><br>' +
				'<p>Vollmacht Frau yz</p><br>'
			cur_frm.set_value('brieftext', brieftext_string);
		} else if (cur_frm.doc.mahnstufe_1 && !cur_frm.doc.mahnstufe_2) {
			var brieftext_string = '<p><b>Herausgabe des vollständigen Patientendossiers</b></p><br>' +
				'<p>Sehr geehrter Herr Professor Müller</p><br>' +
				'<p>Mit Schreiben vom 1. Januar 2012 haben wir im Auftrag von Herrn Muster von Ihnen verlangt, uns das Patientendossier betreffend Eingriff vom 1. Februar 2010 herauszugeben.</p><br>' +
				'<p>Leider haben wir die gewünschten Unterlagen noch nicht erhalten. Wir bitten Sie deshalb nochmals höflich, uns <b>das gesamte Patientendossier</b> umgehend zuzustellen.</p>' + 
				'<p>Evtl. zusätzlich: Sollten die Unterlagen bis Ende des Monats nicht bei uns eintreffen, sehen wir uns gezwungen, für die Herausgabe der Akten den Kantonsarzt um Unterstützung zu bitten.</p>' +
				'<p>Freundliche Grüsse</p>'
			cur_frm.set_value('brieftext', brieftext_string);
		} else if (cur_frm.doc.mahnstufe_2) {
			var brieftext_string = '<p><b>Herausgabe des vollständigen Patientendossiers</b></p><br>' +
				'<p>Sehr geehrter Herr Prof.</p><br>' +
				'<p>Wir kommen zurück auf unsere beiden Schreiben vom 1. Januar und 1. Februar 2012, mit denen wir Sie im Auftrag von Herrn Muster darum ersucht haben, uns die gesamte Krankengeschichte zuzustellen.</p><br>' +
				'<p>Bis heute haben wir von Ihnen die gewünschten Unterlagen nicht erhalten. Wir bitten Sie deshalb ein drittes Mal, um die umgehende Zusendung der uns zustehenden Akten.</p><br>' + 
				'<p>Sollten wir die gewünschten medizinischen Unterlagen bis <b>spätestens Mitte April 2012</b> immer noch nicht erhalten haben, sehen wir uns leider gezwungen, einen externen Rechtsanwalt zu beauftragen, die Herausgabe der Krankengeschichte auf dem Rechtsweg zu erwirken, unter Kostenfolgen zu Ihren Lasten.</p>' +
				'<p>Freundliche Grüsse</p>'
			cur_frm.set_value('brieftext', __(brieftext_string));
		}
	}
}

function timesheet_handling(frm) {
	frappe.prompt([
		{'fieldname': 'datum', 'fieldtype': 'Date', 'label': 'Datum', 'reqd': 1, 'default': 'Today'},
		{'fieldname': 'time', 'fieldtype': 'Float', 'label': 'Arbeitszeit (in h)', 'reqd': 1},
		{'fieldname': 'remark', 'fieldtype': 'Small Text', 'label': __('Bemerkung'), 'reqd': 0}
	],
	function(values){
		frappe.call({
			"method": "spo.utils.timesheet_handlings.create_ts_entry",
			"args": {
				"user": frappe.session.user_email,
				"doctype": frm.doc.doctype,
				"record": frm.doc.name,
				"time": values.time,
				"datum": values.datum,
				"bemerkung": (values.remark||'')
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

function set_kunden_html(frm) {
	if (cur_frm.doc.customer && cur_frm.doc.kunden_kontakt && cur_frm.doc.kunden_adresse) {
		frappe.call({
			"method": "spo.spo.doctype.anforderung_patientendossier.anforderung_patientendossier.get_kunden_data",
			"args": {
				"kunde": cur_frm.doc.customer,
				"adresse": cur_frm.doc.kunden_adresse,
				"kontakt": cur_frm.doc.kunden_kontakt
			},
			"async": false,
			"callback": function(r) {
				cur_frm.set_df_property('kunden_display','options', r.message);
			}
		});
	}
}

function set_titelzeile(frm) {
	if (cur_frm.doc.customer && cur_frm.doc.kunden_kontakt && cur_frm.doc.kunden_adresse) {
		frappe.call({
			"method": "spo.spo.doctype.anforderung_patientendossier.anforderung_patientendossier.get_titelzeile",
			"args": {
				"adresse": cur_frm.doc.kunden_adresse,
				"kontakt": cur_frm.doc.kunden_kontakt
			},
			"async": false,
			"callback": function(r) {
				cur_frm.set_value('titelzeile', r.message);
			}
		});
	}
}
