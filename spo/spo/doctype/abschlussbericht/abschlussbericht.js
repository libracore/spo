// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

var make_default_ts_entry = false;

frappe.ui.form.on('Abschlussbericht', {
	refresh: function(frm) {
		// filter
		cur_frm.fields_dict['titel_textkonserve'].get_query = function(doc) {
			 return {
				 filters: {
					 "mitarbeiter": frappe.user.name,
					 "dokument": "Abschlussbericht - Titelzeile"
				 }
			 }
		};
		cur_frm.fields_dict['textkonserve'].get_query = function(doc) {
			 return {
				 filters: {
					 "mitarbeiter": frappe.user.name,
					 "dokument": "Abschlussbericht - Brieftext"
				 }
			 }
		};
		cur_frm.fields_dict['empfaenger_kontakt'].get_query = function(doc) {
			return {
				filters: {
					"link_doctype": "Customer",
					"link_name": frm.doc.empfaenger
				}
			}
		};
		cur_frm.fields_dict['empfaenger_adresse'].get_query = function(doc) {
			return {
				filters: {
					"link_doctype": "Customer",
					"link_name": frm.doc.empfaenger
				}
			}
		};
		cur_frm.fields_dict['empfaenger'].get_query = function(doc) {
			return {
				filters: {
					"disabled": 0
				}
			}
		};
		// timer action icon
		cur_frm.page.add_action_icon(__("fa fa-history"), function() {
			timesheet_handling(frm);
		});
		
		if (cur_frm.doc.mandat) {
			frm.add_custom_button(__("Zurück zum Mandat"), function() {
				frappe.set_route("Form", "Mandat", cur_frm.doc.mandat);
			});
		}
		set_kunden_html(frm);
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
		set_kunden_html(frm);
		if (cur_frm.is_new()) {
			make_default_ts_entry = true;
		}
	},
	empfaenger: function(frm) {
		cur_frm.set_value("empfaenger_kontakt", "");
		cur_frm.set_value("empfaenger_adresse", "");
		if (cur_frm.doc.empfaenger) {
			frappe.db.get_value('Customer', {'name': cur_frm.doc.empfaenger}, ['customer_name', 'customer_type'], (r) => {
				if (r.customer_type == 'Company') {
					cur_frm.set_value("adressat", r.customer_name);
				}
			});
		}
	},
	empfaenger_kontakt: function(frm) {
		if (cur_frm.doc.empfaenger_kontakt) {
			frappe.db.get_value('Contact', {'name': cur_frm.doc.empfaenger_kontakt}, ['salutation', 'first_name', 'last_name'], (kontakt) => {
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
				cur_frm.set_value("adressat", adresse);
			});
		}
	},
	empfaenger_adresse: function(frm) {
		if (cur_frm.doc.empfaenger_adresse) {
			frappe.db.get_value('Address', {'name': cur_frm.doc.empfaenger_adresse}, ['address_line1', 'address_line2', 'plz', 'city'], (adressen_link) => {
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
	if (cur_frm.doc.mandat) {
		frappe.call({
            "method": "frappe.client.get",
            "args": {
                "doctype": "Mandat",
                "name": frm.doc.mandat
            },
            "callback": function(response) {
                var mandat = response.message;

                if (mandat) {
                    frappe.call({
						"method": "spo.spo.doctype.anforderung_patientendossier.anforderung_patientendossier.get_kunden_data",
						"args": {
							"kunde": mandat.mitglied,
							"adresse": mandat.adresse,
							"kontakt": mandat.kontakt
						},
						"async": false,
						"callback": function(r) {
							cur_frm.set_df_property('kunden_display','options', r.message);
						}
					});
                }
				
				// fetch auftrtaggeber from mandat as empfaenger
				if (!cur_frm.doc.adressat) {
					if (mandat.rsv) {
						cur_frm.set_value("empfaenger", mandat.rsv);
					}
					if (mandat.rsv_kontakt) {
						cur_frm.set_value("empfaenger_kontakt", mandat.rsv_kontakt);
					}
					if (mandat.rsv_adresse) {
						cur_frm.set_value("empfaenger_adresse", mandat.rsv_adresse);
					}
				}
            }
        });
	} else {
		cur_frm.set_df_property('kunden_display','options', '<div><h4>Kein verknüpftes Mandat</h4><p>');
	}
}
