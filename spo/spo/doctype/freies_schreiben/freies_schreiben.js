// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Freies Schreiben', {
	refresh: function(frm) {
		//Set filter to link fields
		set_link_filter(frm);
		// timer action icon
		cur_frm.page.add_action_icon(__("fa fa-history"), function() {
			timesheet_handling(frm);
		});
	},
	empfaenger: function(frm) {
		cur_frm.set_value("kontakt", "");
		cur_frm.set_value("adressen_link", "");
		if (cur_frm.doc.empfaenger) {
			frappe.db.get_value('Customer', {'name': cur_frm.doc.empfaenger}, ['customer_name', 'customer_type'], (r) => {
				if (r.customer_type == 'Company') {
					cur_frm.set_value("adresse", r.customer_name);
				}
			});
		}
	},
	kontakt: function(frm) {
		if (cur_frm.doc.kontakt) {
			frappe.db.get_value('Contact', {'name': cur_frm.doc.kontakt}, ['salutation', 'first_name', 'last_name'], (kontakt) => {
				var adresse = '';
				if (cur_frm.doc.adresse) {
					adresse = cur_frm.doc.adresse;
					adresse += '\n';
				}
				if (kontakt.salutation) {
					adresse += kontakt.salutation;
					adresse += '\n';
				}
				adresse += kontakt.first_name;
				adresse += ' ';
				adresse += kontakt.last_name;
				cur_frm.set_value("adresse", adresse);
			});
		}
	},
	adressen_link: function(frm) {
		if (cur_frm.doc.adressen_link) {
			frappe.db.get_value('Address', {'name': cur_frm.doc.adressen_link}, ['address_line1', 'address_line2', 'plz', 'city'], (adressen_link) => {
				var adresse = '';
				if (cur_frm.doc.adresse) {
					adresse = cur_frm.doc.adresse;
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
				cur_frm.set_value("adresse", adresse);
			});
		}
	}
});

function set_link_filter(frm) {
	cur_frm.fields_dict['kontakt'].get_query = function(doc) {
		return {
			filters: {
				"link_doctype": "Customer",
				"link_name": frm.doc.empfaenger
			}
		}
	};
	cur_frm.fields_dict['adressen_link'].get_query = function(doc) {
		return {
			filters: {
				"link_doctype": "Customer",
				"link_name": frm.doc.empfaenger
			}
		}
	};
	cur_frm.fields_dict['textkonserve'].get_query = function(doc) {
		 return {
			 filters: {
				 "mitarbeiter": frappe.user.name,
				 "dokument": "Freies Schreiben"
			 }
		 }
	}
}

function timesheet_handling(frm) {
	frappe.prompt([
		{'fieldname': 'datum', 'fieldtype': 'Date', 'label': 'Datum', 'reqd': 1, 'default': 'Today'},
		{'fieldname': 'time', 'fieldtype': 'Float', 'label': 'Arbeitszeit (in h)', 'reqd': 1}  
	],
	function(values){
		frappe.call({
			"method": "spo.utils.timesheet_handlings.create_ts_entry",
			"args": {
				"user": frappe.session.user_email,
				"doctype": frm.doc.doctype,
				"record": frm.doc.name,
				"time": values.time,
				"datum": values.datum
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