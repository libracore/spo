// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Medizinischer Bericht', {
	refresh: function(frm) {
		// timer action icon
		cur_frm.page.add_action_icon(__("fa fa-history"), function() {
			timesheet_handling(frm);
		});
		
		if (cur_frm.doc.mandat) {
			frm.add_custom_button(__("Zurück zum Mandat"), function() {
				frappe.set_route("Form", "Mandat", cur_frm.doc.mandat);
			});
		}
		fetch_deckblatt_data(frm);
	},
	onload: function(frm) {
		fetch_deckblatt_data(frm);
	}
});

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
	'Arbeitszeit erfassen',
	'Erfassen'
	)
}

function fetch_deckblatt_data(frm) {
	if (cur_frm.doc.mandat) {
		frappe.call({
            "method": "spo.spo.doctype.medizinischer_bericht.medizinischer_bericht.get_deckblat_data",
            "args": {
                "mandat": cur_frm.doc.mandat
            },
            "callback": function(response) {
                var details = response.message;
				if (details) {
                    if (!cur_frm.doc.klient) {
						cur_frm.set_value('klient', details.name_klient + ", " + details.geburtsdatum_klient);
					}
					cur_frm.set_value('beraterin', details.beraterin);
					cur_frm.set_value('rsv', details.rsv);
					cur_frm.set_value('rsv_kontakt', details.rsv_kontakt);
                }
            }
        });
	}
}
