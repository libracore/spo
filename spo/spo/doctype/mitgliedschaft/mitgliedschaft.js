// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mitgliedschaft', {
    refresh: function(frm) {
        //add btn to create invoice
        if (!frm.doc.rechnung) {
            frm.add_custom_button(__("Erstelle Rechnung"), function() {
                create_invoice(frm);
            });
        }
        
        if ((!cur_frm.doc.not_renew)&&(cur_frm.doc.status == 'Aktiv')) {
            frm.add_custom_button(__("Verlängerung"), function() {
                verlaengerung(frm);
            });
            frm.add_custom_button(__("Kündigung"), function() {
                kuendigung(frm);
            });
            frm.add_custom_button(__("Inaktivierung"), function() {
                inaktivierung(frm);
            });
        }
        cur_frm.fields_dict['mitglied'].get_query = function(doc) {
            return {
                filters: {
                    "disabled": 0
                }
            }
        };
        cur_frm.fields_dict['customer'].get_query = function(doc) {
            return {
                filters: {
                    "disabled": 0
                }
            }
        };
        cur_frm.fields_dict['rechnungsempfaenger'].get_query = function(doc) {
            return {
                filters: {
                    "disabled": 0
                }
            }
        };
    }
});

function create_invoice(frm) {
    frappe.call({
        "method": "spo.spo.doctype.mitgliedschaft.mitgliedschaft.create_invoice",
        "args": {
            "mitgliedschaft": frm.doc.name
        },
        "async": false,
        "callback": function(r) {
            if (r.message) {
                cur_frm.set_value('rechnung', r.message);
                cur_frm.save();
                frappe.msgprint(__("Die Rechnung wurde erfolgreich erstellt<br>Bitte nehmen Sie noch die Verbuchung sowie den Versand vor."), __("Rechnung wurde erstellt"));
            }
        }
    });
}

function verlaengerung(frm) {
    if (cur_frm.is_dirty()) {
        frappe.msgprint("Bitte speichern Sie die Mitgliedschaft zuerst.");
    } else {
        frappe.confirm(
            'Wollen Sie diese Mitgliedschaft um ein Jahr verlängern?',
            function(){
                // on yes
                frappe.call({
                    "method": "spo.spo.doctype.mitgliedschaft.mitgliedschaft.verlaengerung",
                    "args": {
                        "mitgliedschaft": frm.doc.name
                    },
                    "async": false,
                    "callback": function(r) {
                        if (r.message) {
                            cur_frm.set_value('neue_mitgliedschaft', r.message);
                            cur_frm.set_value("status_bezugsdatum", frappe.datetime.nowdate());
                            cur_frm.set_value("status", "Verlängert");
                            cur_frm.save();
                            frappe.msgprint(__("Die Mitgliedschaft wurde erfolgreich verlängert"), __("Mitgliedschaft wurde verlängert"));
                        }
                    }
                });
            },
            function(){
                // on no
            }
        )
    }
}

function kuendigung(frm) {
    if (cur_frm.is_dirty()) {
        frappe.msgprint("Bitte speichern Sie die Mitgliedschaft zuerst.");
    } else {
        frappe.prompt([
            {'fieldname': 'kuendigung', 'fieldtype': 'Date', 'label': 'Kündigung per', 'reqd': 1}  
        ],
        function(values){
            cur_frm.set_value("status_bezugsdatum", frappe.datetime.nowdate());
            cur_frm.set_value("status", "Kündigung");
            cur_frm.set_value("ende", values.kuendigung);
            cur_frm.set_value("not_renew", 1);
            cur_frm.save();
            frappe.msgprint(__("Die Mitgliedschaft wurde erfolgreich gekündet"), __("Mitgliedschaft wurde gekündet"));
        },
        'Mitgliedschafts Kündigung',
        'Künden'
        )
    }
}

function inaktivierung(frm) {
    if (cur_frm.is_dirty()) {
        frappe.msgprint("Bitte speichern Sie die Mitgliedschaft zuerst.");
    } else {
        frappe.confirm(
            'Wollen Sie diese Mitgliedschaft inaktivieren?',
            function(){
                // on yes
                cur_frm.set_value("status_bezugsdatum", frappe.datetime.nowdate());
                cur_frm.set_value("status", "Inaktiviert");
                cur_frm.set_value("ende", frappe.datetime.nowdate());
                cur_frm.set_value("not_renew", 1);
                cur_frm.save();
                frappe.msgprint(__("Die Mitgliedschaft wurde erfolgreich inaktiviert"), __("Mitgliedschaft wurde inaktiviert"));
            },
            function(){
                // on no
            }
        )
    }
}
