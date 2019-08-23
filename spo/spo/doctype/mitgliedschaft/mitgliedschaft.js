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
				frappe.msgprint("Die Rechnung wurde erfolgreich erstellt<br>Bitte nehmen Sie noch die Verbuchung sowie den Versand vor.", "Rechnung wurde erstellt");
			}
		}
	});
}
