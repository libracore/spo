// Copyright (c) 2021, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Beratungsslot', {
    refresh: function(frm) {
        if (frm.doc.payrexx_id) {
            frm.add_custom_button(__("Zahlungsstatus aktualisieren"), function() {
                frappe.call({
                    'method': 'fetch_payment_status',
                    'doc': frm.doc,
                    'callback': function(response) {
                       frappe.show_alert( __("Aktualisiert") );
                       cur_frm.reload_doc();
                    }
                });
            });
        }
    }
});
