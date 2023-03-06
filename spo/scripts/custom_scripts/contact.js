frappe.ui.form.on('Contact', {
    erstelle_rsv_upload_login: function(frm) {
        frappe.call({
            method: 'spo.scripts.custom_scripts.customer.get_rsv_upload_cred',
            args: {
                contact: cur_frm.doc.name
            },
            callback: function(r) {
                if(r.message) {
                    cur_frm.set_value("rsv_upload_login", r.message.login);
                    cur_frm.set_value("rsv_upload_url", r.message.url);
                } 
            }
        });
    }
});
