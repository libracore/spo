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
			{'fieldname': 'mandat', 'fieldtype': 'Link', 'label': __('Mandat'), 'reqd': 1, 'options': 'Mandat'}  
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
			if (!rsv && !cur_frm.doc.customer) {
				frappe.msgprint(__("Bitte wählen Sie zuerst einen Kunden aus, da im Mandat keine RSV hinterlegt ist."));
				return
			} else {
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
					cur_frm.refresh_field('items');
					for (i=0; i<logs.length; i++) {
						var child = cur_frm.add_child('items');
						frappe.model.set_value(child.doctype, child.name, 'item_code', 'Mandatsverrechnung');
						frappe.model.set_value(child.doctype, child.name, 'qty', logs[i].hours);
						frappe.model.set_value(child.doctype, child.name, 'spo_description', logs[i].spo_remark);
						frappe.model.set_value(child.doctype, child.name, 'spo_datum', logs[i].from_time);
						cur_frm.refresh_field('items');
					}
					var df = frappe.meta.get_docfield("Sales Invoice Item","description", cur_frm.doc.name);
					df.hidden = 1;
					frappe.msgprint(__("Bitte denken Sie daran, dass Sie prüfen müssen ob zu diesem Mandat Drittleistungen verrechnet werden müssen!"), __('Drittleistungen'));
				}
			}
		}
	});
}