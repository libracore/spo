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
				if (cur_frm.doc.asap_print == 1) {
					if (cur_frm.doc.rechnungen_erstellt == 0 && cur_frm.doc.pdf_erstellt == 0) {
						cur_frm.set_intro("<br>Das System erstellt für alle aufgeführten Mitgliedschaften eine neue einjährige Mitgliedschaft sowie jeweils eine Mitgliederrechnung und verbucht diese.<br>Sie können den Fortschrit --><a href='/desk#background_jobs'>hier</a><-- verfolgen.<br>Im Anschluss wird das System ein PDF generieren Welches alle hierbei erstellten Rechnungen beinhaltet und heruntergeladen werden kann.");
					}
					if (cur_frm.doc.rechnungen_erstellt == 1 && cur_frm.doc.pdf_erstellt == 0) {
						cur_frm.set_intro("<br>Das System hat für alle aufgeführten Mitgliedschaften eine neue einjährige Mitgliedschaft sowie jeweils eine Mitgliederrechnung erstellt und verbucht.<br>Nun erstellt das System für alle soeben erstellten/verbuchten Rechnungen ein PDF, Sie können den Fortschrit --><a href='/desk#background_jobs'>hier</a><-- verfolgen.<br>Sobald der Backgroundjob abgeschlossen ist können Sie das erstellte PDF herunterladen.");
					}
					if (cur_frm.doc.rechnungen_erstellt == 1 && cur_frm.doc.pdf_erstellt == 1) {
						cur_frm.set_intro('<br>Das PDF wurde erfolgreich erstellt.<br>Sie können es mit einem Klick, oben rechts auf "Rechnungen als PDF", herunterladen.');
						frm.add_custom_button(__("Rechnungen als PDF"), function() {
							download(frm);
						});
					}
				} else {
					cur_frm.set_intro("<br>Das System erstellt für alle aufgeführten Mitgliedschaften eine neue einjährige Mitgliedschaft sowie jeweils eine Mitgliederrechnung.<br>Sie können den Fortschrit --><a href='/desk#background_jobs'>hier</a><-- verfolgen.<br>Sobald der Backgroundjob abgeschlossen ist müssen Sie die Rechnungen verbuchen, drucken und versenden.");
				}
			}
		} else {
			cur_frm.set_intro("Speichern Sie diesen Rechnungslauf um alle auslaufenden Mitgliedschaften zu laden.");
		}
	}
});

function download(frm) {
  var element = document.createElement('a');
  element.setAttribute('href', '/assets/spo/sinvs_for_print/Rechnungslauf_' + frm.doc.name + '.pdf');
  element.setAttribute('download', 'Rechnungslauf_' + frm.doc.name);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}