// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mitglieder Rechnungslauf', {
	refresh: function(frm) {
		if (!cur_frm.is_new()) {
			if (cur_frm.doc.docstatus == 0) {
				cur_frm.set_intro("<br>Durch das Buchen werden für alle aufgeführten Mitgliedschaften eine neue einjährige Mitgliedschaft sowie jeweils eine Mitgliederrechnung erstellt.<br>Die maximale Anzahl Mitgliedschaften die pro Rechnungslauf verarbeitet werden können liegt bei 500.");
			}
			if (cur_frm.doc.docstatus == 1) {
				cur_frm.set_intro("<br>Durch das Buchen wurden für alle aufgeführten Mitgliedschaften eine neue einjährige Mitgliedschaft sowie jeweils eine Mitgliederrechnung erstellt.<br>Die erstellten Rechnungen müssen nun noch verbucht, gedruckt und versendet werden.");
			}
		}
	}
});
