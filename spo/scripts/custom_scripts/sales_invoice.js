frappe.ui.form.on('Sales Invoice', {
	refresh: function(frm) {
        frm.add_custom_button(__("Erstelle Mandats-Rechnung"), function() {
            create_mandats_rechnung(frm);
        });
    }
});

function create_mandats_rechnung(frm) {
	frappe.prompt(
		[
			{'fieldname': 'mandat', 'fieldtype': 'Link', 'label': 'Mandat', 'reqd': 1, 'options': 'Mandat'}  
		],
		function(values){
			get_mandats_positionen(frm, values.mandat);
		},
		'Für welches Mandat soll eine Rechnung erstellt werden?',
		'Lade Mandats-Positionen'
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
				frappe.msgprint("Bitte wählen Sie zuerst einen Kunden aus, da im Mandat keine RSV hinterlegt ist.");
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
						frappe.model.set_value(child.doctype, child.name, 'item_code', 'Buch-XYZ');
						frappe.model.set_value(child.doctype, child.name, 'qty', logs[i].hours);
						frappe.model.set_value(child.doctype, child.name, 'spo_description', logs[i].spo_remark);
						cur_frm.refresh_field('items');
					}
				}
			}
		}
	});
}