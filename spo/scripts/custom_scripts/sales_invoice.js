frappe.ui.form.on('Sales Invoice', {
	refresh: function(frm) {
        frm.add_custom_button(__("Erstelle Mandats-Rechnung"), function() {
            create_mandats_rechnung(frm);
        });
		if (cur_frm.doc.mandat) {
			var df = frappe.meta.get_docfield("Sales Invoice Item","description", cur_frm.doc.name);
			df.hidden = 1;
		}
    },
	validate: function(frm) {
		if ((!cur_frm.doc.is_return)&&(cur_frm.doc.company == 'Gönnerverein')) {
			update_esr(frm);
		}
	}
});

function update_esr(frm) {
	frappe.call({
		"method": "spo.utils.esr.set_esr_reference_and_esr_code",
		"args": {
			"sinv": cur_frm.doc.name,
			"customer": cur_frm.doc.customer,
			"grand_total": parseFloat(cur_frm.doc.grand_total)
		},
		"async": false,
		"callback": function(r) {
			if (r.message) {
				cur_frm.set_value('esr_reference', r.message.esr_reference);
				cur_frm.set_value('esr_code', r.message.esr_code);
			}
		}
	});
}

function create_mandats_rechnung(frm) {
	frappe.prompt(
		[
			{'fieldname': 'mandat', 'fieldtype': 'Link', 'label': __('Mandat'), 'reqd': 1, 'options': 'Mandat', 'default': cur_frm.doc.mandat}  
		],
		function(values){
			get_mandats_positionen(frm, values.mandat);
		},
		__('Für welches Mandat soll eine Rechnung erstellt werden?'),
		__('Lade Mandats-Positionen')
	)
}

function get_mandats_positionen(frm, mandat) {
	frappe.call({
		"method": "spo.utils.mandat_invoice.get_mandat_logs",
		"args": {
			"mandat": mandat
		},
		"async": false,
		"callback": function(response) {
			console.log(response.message.logs);
			var logs = response.message.logs;
			var rsv = response.message.rsv;
			var rate = response.message.rate;
			if (!rate || rate <= 0) {
				rate = false;
			}
			if (!rsv && !cur_frm.doc.customer) {
				frappe.msgprint(__("Bitte wählen Sie zuerst einen Kunden aus, da im Mandat keine RSV hinterlegt ist."));
				return
			} else {
				frappe.msgprint(__("Bitte warten Sie, die Mandatspositionen werden geladen..."), __('Bitte warten...'));
				cur_frm.set_value('mandat', mandat);
				if (rsv) {
					cur_frm.set_value('customer', rsv);
				}
				if (logs) {
					var i;
					var tbl = cur_frm.doc.items || [];
					var i = tbl.length;
					while (i--)
					{
						cur_frm.get_field("items").grid.grid_rows[i].remove();
					}
					for (i=0; i<logs.length; i++) {
						var child = cur_frm.add_child('items');
						var beschreibung = '';
						if (logs[i].spo_dokument) {
							beschreibung = beschreibung + __(logs[i].spo_dokument) + "; ";
						}
						if (logs[i].spo_remark) {
							beschreibung = beschreibung + logs[i].spo_remark;
						} else {
							beschreibung = beschreibung + __('erstellt');
						}
						frappe.model.set_value(child.doctype, child.name, 'item_code', 'Mandatsverrechnung');
						frappe.model.set_value(child.doctype, child.name, 'qty', logs[i].hours);
						frappe.model.set_value(child.doctype, child.name, 'spo_description', beschreibung);
						frappe.model.set_value(child.doctype, child.name, 'spo_datum', logs[i].from_time);
						frappe.model.set_value(child.doctype, child.name, 'income_account', '3100 - Beratungseinnahmen 6.1% - SPO');
						frappe.model.set_value(child.doctype, child.name, 'cost_center', 'Main - SPO');
                        frappe.model.set_value(child.doctype, child.name, 'employee', logs[i].employee_name);
					}
					if (rate) {
						cur_frm.save().then(() => {
							var line_items = cur_frm.doc.items;
							line_items.forEach(function(entry) {
								 entry.rate = rate;
							});
							var df = frappe.meta.get_docfield("Sales Invoice Item","description", cur_frm.doc.name);
							df.hidden = 1;
							
							cur_frm.save().then(() => {
								frappe.msgprint(__("Die Mandatspositionen wurden erfolgreich geladen.<br>Bitte denken Sie daran, dass Sie prüfen müssen ob zu diesem Mandat Drittleistungen verrechnet werden müssen!"), __('Drittleistungen'));
							});
						});
					} else {
						var df = frappe.meta.get_docfield("Sales Invoice Item","description", cur_frm.doc.name);
						df.hidden = 1;
						cur_frm.save().then(() => {
							frappe.msgprint(__("Die Mandatspositionen wurden erfolgreich geladen.<br>Bitte denken Sie daran, dass Sie prüfen müssen ob zu diesem Mandat Drittleistungen verrechnet werden müssen!"), __('Drittleistungen'));
						});
					}
				}
			}
		}
	});
}