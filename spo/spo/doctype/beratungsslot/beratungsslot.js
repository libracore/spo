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
        // filter for berater based on topic
        cur_frm.fields_dict['user'].get_query = function(doc) {          
             return {
                 filters: {
                     "objective": frm.doc.topic 
                 }
             }
        }
    },
    customer: function(frm) {
        if (!frm.doc.customer) {
            cur_frm.set_value("customer_name", null);
        }
    }
});
