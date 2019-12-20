// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

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
		// timer action icon
		cur_frm.page.add_action_icon(__("fa fa-history"), function() {
			timesheet_handling(frm);
		});
		
		defaul_texte(frm);
	},
	onload: function(frm) {
		defaul_texte(frm);
	},
	mahnstufe_1: function(frm) {
		defaul_texte(frm);
	},
	mahnstufe_2: function(frm) {
		defaul_texte(frm);
	}
});

function defaul_texte(frm) {
	if (!cur_frm.doc.textbaustein && !cur_frm.doc.text_ohne_konserve) {
		if (!cur_frm.doc.mahnstufe_1  && !cur_frm.doc.mahnstufe_2) {
			var brieftext_string = '<p><b>Herr M. L., Geb, Datum und Adresse<br>Herausgabe Patientendossier - Onkologie, Behandlung seit November 2016</b></p><br>' +
				'<p>Sehr geehrter Herr Dr. Chaksad</p><br>' +
				'<p>Herr M. … wandte sich an die Stiftung SPO Patientenschutz und bat uns für ihn folgende Unterlagen zu verlangen:</p><br>' +
				'<ul><li><b>vollständiges Patientendossier seit 21.11.2016 mit:</b>' +
				'<ul><li>Verlaufsberichte Chemotherapie (ambulant und stationär)</li>' +
				'<li>Untersuchungsberichte / Konsiliarberichte (Medizin/Chirurgie)</li>' +
				'<li>Pflegedokumentation (Pflegebericht, Überwachungsblätter und Kardex)</li>' +
				'<li>Verordnungsblätter</li>' +
				'<li>Laborbefunde, Ultrschallberichte, Röntgenbefunde und Röntgenbilder auf CD</li>' +
				'<li>Verlegungsbericht Onkologie -> Viszeralchirurgie.</li></ul></li></ul><br>' +
				'<p>Wir danken Ihnen für die baldige Zusendung.</p><br>' +
				'<p>Freundliche Grüsse</p><br><br><br>' +
				'<table style="width: 100%;"><tr><td>Beilage:</td><td>Vollmacht</td></tr><tr><td>Kopie an:</td><td>Herrn L. M.</td></tr></table>';
				
			cur_frm.set_value('brieftext', brieftext_string);
		} else if (cur_frm.doc.mahnstufe_1 && !cur_frm.doc.mahnstufe_2) {
			var brieftext_string = '<p><b>Martin Muster, Musterstrasse 4, 8000 Muster<br>Herausgabe des vollständigen Patientendossiers</b></p><br>' +
				'<p>Sehr geehrter Herr Professor Müller</p><br>' +
				'<p>Mit Schreiben vom 1. Januar 2012 haben wir im Auftrag von Herrn Muster von Ihnen verlangt, uns das Patientendossier betreffend Eingriff vom 1. Februar 2010 herauszugeben.</p><br>' +
				'<p>Leider haben wir die gewünschten Unterlagen noch nicht erhalten. Wir bitten Sie deshalb nochmals höflich, uns <b>das gesamte Patientendossier</b> umgehend zuzustellen.</p>' + 
				'<p>Evtl. zusätzlich: Sollten die Unterlagen bis Ende des Monats nicht bei uns eintreffen, sehen wir uns gezwungen, für die Herausgabe der Akten den Kantonsarzt um Unterstützung zu bitten.</p>' +
				'<p>Freundliche Grüsse</p><br><br><br>' +
				'<table style="width: 100%;"><tr><td>Beilage:</td><td>Vollmacht</td></tr><tr><td>Kopie an:</td><td>Herrn L. M.</td></tr></table>';
				
			cur_frm.set_value('brieftext', brieftext_string);
		} else if (cur_frm.doc.mahnstufe_2) {
			var brieftext_string = '<p><b>Martin Muster, Musterstrasse 4, 8000 Muster<br>Herausgabe des vollständigen Patientendossiers</b></p><br>' +
				'<p>Sehr geehrter Herr Prof.</p><br>' +
				'<p>Wir kommen zurück auf unsere beiden Schreiben vom 1. Januar und 1. Februar 2012, mit denen wir Sie im Auftrag von Herrn Muster darum ersucht haben, uns die gesamte Krankengeschichte zuzustellen.</p><br>' +
				'<p>Bis heute haben wir von Ihnen die gewünschten Unterlagen nicht erhalten. Wir bitten Sie deshalb ein drittes Mal, um die umgehende Zusendung der uns zustehenden Akten.</p><br>' + 
				'<p>Sollten wir die gewünschten medizinischen Unterlagen bis <b>spätestens Mitte April 2012</b> immer noch nicht erhalten haben, sehen wir uns leider gezwungen, einen externen Rechtsanwalt zu beauftragen, die Herausgabe der Krankengeschichte auf dem Rechtsweg zu erwirken, unter Kostenfolgen zu Ihren Lasten.</p>' +
				'<p>Freundliche Grüsse</p><br><br><br>' +
				'<table style="width: 100%;"><tr><td>Kopie:</td><td>- falls Arzt Mitglied der FMH:  Rechtsabteilung FMH in Bern	oder Kopie an</td></tr><tr><td> </td><td>- Kantonsarzt</td></tr><tr><td> </td><td>- oder jeweilige Fachgesellschaft</td></tr><tr><td> </td><td>- Martin Muster</td></tr></table>';
				
			cur_frm.set_value('brieftext', brieftext_string);
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