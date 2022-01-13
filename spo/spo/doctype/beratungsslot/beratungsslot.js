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
        } else {
            if ((frm.doc.customer) && (!frm.doc.__islocal)) {
                frm.add_custom_button(__("Rechnung erstellen"), function() {
                    frappe.call({
                        'method': 'spo.utils.onlinetermin.submit_request',
                        'args': {
                            'slot': frm.doc.name, 
                            'member': frm.doc.customer, 
                            'first_name': frm.doc.first_name || "", 
                            'last_name': frm.doc.last_name || "", 
                            'address': frm.doc.address || "", 
                            'city': frm.doc.city || "", 
                            'pincode': frm.doc.pincode || "", 
                            'email': frm.doc.email_id || "", 
                            'phone': frm.doc.phone || "",
                            'geburtsdatum': frm.doc.geburtsdatum || "",
                            'salutation_title': frm.doc.salutation_title || "",
                        },
                        'callback': function(response) {
                            // invoice created
                            cur_frm.doc.reload_doc();
                            cur_frm.refresh();
                        }
                    });
                });
            }
        }
        // filter for berater based on topic
        cur_frm.fields_dict['user'].get_query = function(doc) {          
             return {
                 filters: {
                     "objective": frm.doc.topic 
                 }
             }
        }
        if (frm.doc.customer) {
            frm.add_custom_button(__("Anfrage erstellen"), function() {
                frappe.route_options = {
                    "customer": frm.doc.customer,
                    "anfrage_typ": "Online-Beratung",
                    "kontakt_via": "Telefon"
                }
                frappe.set_route("List", "Anfrage");
            });
        }
    },
    customer: function(frm) {
        if (!frm.doc.customer) {
            cur_frm.set_value("customer_name", null);
        }
    }
});


