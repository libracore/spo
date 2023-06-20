cur_frm.dashboard.add_transactions([
    {
        'label': 'SPO Referenzen',
        'items': [
            'Anfrage',
            'Mandat',
            'Mitgliedschaft',
            'Freies Schreiben',
            'Beratungsslot'
        ]
    }
]);

frappe.ui.form.on('Customer', {
    refresh: function(frm) {
        frappe.call({
            method: 'spo.scripts.custom_scripts.customer.get_spenden',
            args: {
                customer: cur_frm.doc.name
            },
            callback: function(r) {
                if(r.message) {
                    var spenden_html = '<h3>Spendenübersicht</h3><div class="row"><div class="col-xs-6">Aktuelles Jahr:<br>CHF ' + parseFloat(r.message.aktuell) + '</div><div class="col-xs-6">Letzte 5 Jahre:<br>CHF ' + parseFloat(r.message.total) + '</div></div>';
                    cur_frm.dashboard.add_section(spenden_html);
                } 
            }
        });
    },
    erstelle_rsv_upload_id: function(frm) {
        frappe.confirm(
            'Sind Sie sicher, dass Sie eine neue RSV-Upload ID erzeugen möchten?<br>Beachten Sie dass der vorgängig erzeugte dadurch ungültig wird.',
            function(){
                // on yes
                frappe.call({
                    method: 'spo.scripts.custom_scripts.customer.get_rsv_upload_cred',
                    args: {
                        customer: cur_frm.doc.name
                    },
                    callback: function(r) {
                        if(r.message) {
                            cur_frm.set_value("rsv_upload_id", r.message.id);
                            cur_frm.set_value("rsv_upload_url", r.message.url);
                        } 
                    }
                });
            },
            function(){
                // on no nothing
            }
        )
        
    }
});
