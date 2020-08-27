// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Facharzt Bericht', {
	refresh: function(frm) {
		set_filters(frm);
		if (!cur_frm.doc.adressat) {
			set_facharzt_adressat(frm);
		}
		if (!cur_frm.doc.patienten_anschrift) {
			set_patient_adressat(frm);
		}
		// timer action icon
		cur_frm.page.add_action_icon(__("fa fa-history"), function() {
			timesheet_handling(frm);
		});
	},
	facharzt_kontakt: function(frm) {
		set_facharzt_adressat(frm);
	},
	facharzt_adresse: function(frm) {
		set_facharzt_adressat(frm);
	},
	patienten_kontakt: function(frm) {
		set_patient_adressat(frm);
	},
	patienten_adresse: function(frm) {
		set_patient_adressat(frm);
	}
});

function set_filters(frm) {
	cur_frm.fields_dict['facharzt_kontakt'].get_query = function(doc) {
		return {
			filters: {
				"link_doctype": "Supplier",
				"link_name": cur_frm.doc.facharzt
			}
		}
	}
	cur_frm.fields_dict['facharzt_adresse'].get_query = function(doc) {
		return {
			filters: {
				"link_doctype": "Supplier",
				"link_name": cur_frm.doc.facharzt
			}
		}
	}
	cur_frm.fields_dict['patienten_kontakt'].get_query = function(doc) {
		return {
			filters: {
				"link_doctype": "Customer",
				"link_name": cur_frm.doc.patient
			}
		}
	}
	cur_frm.fields_dict['patienten_adresse'].get_query = function(doc) {
		return {
			filters: {
				"link_doctype": "Customer",
				"link_name": cur_frm.doc.patient
			}
		}
	}
}

function set_facharzt_adressat(frm) {
	frappe.call({
		"method": "spo.spo.doctype.facharzt_bericht.facharzt_bericht.get_adressat",
		"args": {
			"facharzt": cur_frm.doc.facharzt,
			"facharzt_name": cur_frm.doc.facharzt_name,
			"kontakt": cur_frm.doc.facharzt_kontakt,
			"adresse": cur_frm.doc.facharzt_adresse,
			"typ": "Supplier"
		},
		"async": false,
		"callback": function(r) {
			if (r.message) {
				cur_frm.set_value('adressat', r.message);
			}
		}
	});
}

function set_patient_adressat(frm) {
	console.log("ok");
	frappe.call({
		"method": "spo.spo.doctype.facharzt_bericht.facharzt_bericht.get_adressat",
		"args": {
			"facharzt": cur_frm.doc.patient,
			"facharzt_name": 'Bitte Vor- und Nachnamen eintragen',
			"kontakt": cur_frm.doc.patienten_kontakt,
			"adresse": cur_frm.doc.patienten_adresse,
			"typ": "Customer"
		},
		"async": false,
		"callback": function(r) {
			console.log(r.message);
			if (r.message) {
				cur_frm.set_value('patienten_anschrift', r.message);
			}
		}
	});
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