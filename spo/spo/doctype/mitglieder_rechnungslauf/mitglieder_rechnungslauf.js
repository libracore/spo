// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mitglieder Rechnungslauf', {
	refresh: function(frm) {
		if (!cur_frm.is_new()) {
			cur_frm.refresh_header();
			if (cur_frm.doc.docstatus == 0) {
				cur_frm.set_intro("<br>Durch das Buchen werden für alle aufgeführten Mitgliedschaften eine neue einjährige Mitgliedschaft sowie jeweils eine Mitgliederrechnung erstellt.<br>Die maximale Anzahl Mitgliedschaften die pro Rechnungslauf verarbeitet werden können liegt bei 500.");
			}
			if (cur_frm.doc.docstatus == 1) {
				cur_frm.set_intro("<br>Durch das Buchen wurden für alle aufgeführten Mitgliedschaften eine neue einjährige Mitgliedschaft sowie jeweils eine Mitgliederrechnung erstellt.<br>Die erstellten Rechnungen müssen nun noch verbucht, gedruckt und versendet werden.");
				if (cur_frm.doc.pdf_erstellt) {
					frm.add_custom_button(__("Rechnungen als PDF"), function() {
						download(frm);
					});
				}
			}
		} else {
			cur_frm.set_intro("Speichern Sie diesen Rechnungslauf um alle auslaufenden Mitgliedschaften zu laden.");
		}
	}
});

function print_rechnungen(frm) {
	/* frappe.call({
		"method": "frappe.utils.print_format.download_multi_pdf",
		"args": {
			"doctype": {"Sales Invoice": frm.doc.rechnungen},
			"name": "rechnungslauf_test"
		},
		"callback": function(r) {
			if (r) {
				frappe.msgprint("okdok");
			}
		}
	}); */
}


function download(frm) {
  var element = document.createElement('a');
  element.setAttribute('href', '/assets/spo/sinvs_for_print/Rechnungslauf_' + frm.doc.name + '.pdf');
  element.setAttribute('download', 'Rechnungslauf_' + frm.doc.name);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}