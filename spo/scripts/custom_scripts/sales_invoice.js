frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        if (!cur_frm.doc.mandat&&!cur_frm.doc.meldestelle) {
            frm.add_custom_button(__("Erstelle Mandats-Rechnung"), function() {
                create_mandats_rechnung(frm);
            }, __("Erstelle"));
            frm.add_custom_button(__("Erstelle Meldestelle-Rechnung"), function() {
                create_meldestelle_rechnung(frm);
            }, __("Erstelle"));
        }
        if (cur_frm.doc.mandat||cur_frm.doc.meldestelle) {
            var df = frappe.meta.get_docfield("Sales Invoice Item","description", cur_frm.doc.name);
            df.hidden = 1;
        }
    },
    validate: function(frm) {
        if ((!frm.doc.__islocal)&&(!cur_frm.doc.is_return)&&(cur_frm.doc.company == 'Gönnerverein')) {
            update_esr(frm);
        }
    }
});

function update_esr(frm) {
    frappe.call({
        "method": "spo.utils.esr.get_qrr_reference",
        "args": {
            "sales_invoice": cur_frm.doc.name,
            "customer": cur_frm.doc.customer
        },
        "async": false,
        "callback": function(r) {
            if (r.message) {
                cur_frm.set_value('esr_reference', r.message);
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

function create_meldestelle_rechnung(frm) {
    frappe.prompt(
        [
            {'fieldname': 'meldestelle', 'fieldtype': 'Link', 'label': __('Meldestelle'), 'reqd': 1, 'options': 'Meldestelle', 'default': cur_frm.doc.meldestelle}  
        ],
        function(values){
            get_meldestelle_positionen(frm, values.meldestelle);
        },
        __('Für welche Meldestelle Meldung soll eine Rechnung erstellt werden?'),
        __('Lade Meldestelle-Positionen')
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
            var logs = response.message.logs;
            var rsv = response.message.rsv;
            var rate = response.message.rate;
            var ist_pauschal = response.message.ist_pauschal;
            var pauschal_artikel = response.message.pauschal_artikel;
            var pauschal_betrag = response.message.pauschal_betrag;
            var med_abschl_gespr = response.message.med_abschl_gespr;
            var med_abschl_gespr_datum = response.message.med_abschl_gespr_datum;
            var med_jur_abschl_gespr = response.message.med_jur_abschl_gespr;
            var med_jur_abschl_gespr_datum = response.message.med_jur_abschl_gespr_datum;
            var med_abschl_gespr_betrag = response.message.med_abschl_gespr_betrag;
            var med_jur_abschl_gespr_betrag = response.message.med_jur_abschl_gespr_betrag;
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
                        frappe.model.set_value(child.doctype, child.name, 'klientenkontakt', logs[i].klientenkontakt);
                    }
                    
                    //~ Pauschal Verrechnung
                    if (pauschal_artikel&&ist_pauschal) {
                        var child = cur_frm.add_child('items');
                        frappe.model.set_value(child.doctype, child.name, 'item_code', pauschal_artikel);
                        frappe.model.set_value(child.doctype, child.name, 'qty', 1);
                        frappe.model.set_value(child.doctype, child.name, 'spo_description', 'Mandat Pauschalverrechnung');
                        frappe.model.set_value(child.doctype, child.name, 'income_account', '3100 - Beratungseinnahmen 6.1% - SPO');
                        frappe.model.set_value(child.doctype, child.name, 'cost_center', 'Main - SPO');
                    }
                    
                    //~ Medizinisches Abschlussgespräch
                    if (med_abschl_gespr) {
                        var child = cur_frm.add_child('items');
                        frappe.model.set_value(child.doctype, child.name, 'item_code', pauschal_artikel);
                        frappe.model.set_value(child.doctype, child.name, 'qty', 1);
                        frappe.model.set_value(child.doctype, child.name, 'spo_description', 'Medizinisches Abschlussgespräch ' + med_abschl_gespr_datum);
                        frappe.model.set_value(child.doctype, child.name, 'income_account', '3100 - Beratungseinnahmen 6.1% - SPO');
                        frappe.model.set_value(child.doctype, child.name, 'cost_center', 'Main - SPO');
                        frappe.model.set_value(child.doctype, child.name, 'med_abschl_gespr', 1);
                    }
                    
                    //~ Medizinisch Juristische Abschlussgespräch
                    if (med_jur_abschl_gespr) {
                        var child = cur_frm.add_child('items');
                        frappe.model.set_value(child.doctype, child.name, 'item_code', pauschal_artikel);
                        frappe.model.set_value(child.doctype, child.name, 'qty', 1);
                        frappe.model.set_value(child.doctype, child.name, 'spo_description', 'Medizinisch-Juristisches Abschlussgespräch ' + med_jur_abschl_gespr_datum);
                        frappe.model.set_value(child.doctype, child.name, 'income_account', '3100 - Beratungseinnahmen 6.1% - SPO');
                        frappe.model.set_value(child.doctype, child.name, 'cost_center', 'Main - SPO');
                        frappe.model.set_value(child.doctype, child.name, 'med_jur_abschl_gespr', 1);
                    }
                    
                    cur_frm.save().then(() => {
                        var line_items = cur_frm.doc.items;
                        line_items.forEach(function(entry) {
                             //~ Pauschal Verrechnug
                             if (pauschal_artikel&&ist_pauschal) {
                                 if (entry.item_code == pauschal_artikel) {
                                     if (entry.med_abschl_gespr) {
                                         entry.rate = med_abschl_gespr_betrag;
                                     } else if (entry.med_jur_abschl_gespr) {
                                         entry.rate = med_jur_abschl_gespr_betrag;
                                     } else {
                                         entry.rate = pauschal_betrag;
                                     }
                                 } else {
                                     if (entry.klientenkontakt) {
                                         entry.rate = rate;
                                     } else {
                                         entry.rate = 0;
                                         entry.discount_percentage = 100;
                                         entry.discount_amount = entry.price_list_rate;
                                     }
                                 }
                             } else {
                                 if (rate) {
                                     entry.rate = rate;
                                 }
                             }
                        });
                        var df = frappe.meta.get_docfield("Sales Invoice Item","description", cur_frm.doc.name);
                        df.hidden = 1;
                        
                        cur_frm.save().then(() => {
                            frappe.msgprint(__("Die Mandatspositionen wurden erfolgreich geladen.<br>Bitte denken Sie daran, dass Sie prüfen müssen ob zu diesem Mandat Drittleistungen verrechnet werden müssen!"), __('Drittleistungen'));
                        });
                    });
                }
            }
        }
    });
}

function get_meldestelle_positionen(frm, meldestelle) {
    frappe.call({
        "method": "spo.utils.meldestelle_invoice.get_logs",
        "args": {
            "meldestelle": meldestelle
        },
        "async": false,
        "callback": function(response) {
            console.log(response.message.logs);
            var logs = response.message.logs;
            var customer = response.message.customer;
            if (!customer && !cur_frm.doc.customer) {
                frappe.msgprint(__("Bitte wählen Sie zuerst einen Kunden aus, da in der Meldestellen Meldung kein Ersteller hinterlegt ist."));
                return
            } else {
                cur_frm.set_value('customer', customer);
                if (logs) {
                    frappe.msgprint(__("Bitte warten Sie, die Meldestellenpositionen werden geladen..."), __('Bitte warten...'));
                    cur_frm.set_value('meldestelle', meldestelle);
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
                        frappe.model.set_value(child.doctype, child.name, 'item_code', 'Meldestelle');
                        frappe.model.set_value(child.doctype, child.name, 'qty', logs[i].hours);
                        frappe.model.set_value(child.doctype, child.name, 'spo_description', beschreibung);
                        frappe.model.set_value(child.doctype, child.name, 'spo_datum', logs[i].from_time);
                        frappe.model.set_value(child.doctype, child.name, 'income_account', '3150 - Beratungseinnahmen Meldestelle 6.1% - SPO');
                        frappe.model.set_value(child.doctype, child.name, 'cost_center', 'Main - SPO');
                        frappe.model.set_value(child.doctype, child.name, 'employee', logs[i].employee_name);
                    }
                    var df = frappe.meta.get_docfield("Sales Invoice Item","description", cur_frm.doc.name);
                    df.hidden = 1;
                    cur_frm.save().then(() => {
                        frappe.msgprint(__("Die Meldestellenpositionen wurden erfolgreich geladen."), __('Meldestellenpositionen'));
                    });
                }
            }
        }
    });
}
