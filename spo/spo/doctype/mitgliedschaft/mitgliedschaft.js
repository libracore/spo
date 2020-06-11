// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mitgliedschaft', {
	refresh: function(frm) {
		//add btn to create invoice
		if (!frm.doc.rechnung) {
			frm.add_custom_button(__("Erstelle Rechnung"), function() {
				create_invoice(frm);
			});
		}
		cur_frm.fields_dict['mitglied'].get_query = function(doc) {
			return {
				filters: {
					"disabled": 0
				}
			}
		};
		cur_frm.fields_dict['customer'].get_query = function(doc) {
			return {
				filters: {
					"disabled": 0
				}
			}
		};
		cur_frm.fields_dict['rechnungsempfaenger'].get_query = function(doc) {
			return {
				filters: {
					"disabled": 0
				}
			}
		};
	}
});

function create_invoice(frm) {
	frappe.call({
		"method": "spo.spo.doctype.mitgliedschaft.mitgliedschaft.create_invoice",
		"args": {
			"mitgliedschaft": frm.doc.name
		},
		"async": false,
		"callback": function(r) {
			if (r.message) {
				cur_frm.set_value('rechnung', r.message);
				cur_frm.save();
				frappe.msgprint(__("Die Rechnung wurde erfolgreich erstellt<br>Bitte nehmen Sie noch die Verbuchung sowie den Versand vor."), __("Rechnung wurde erstellt"));
			}
		}
	});
}
