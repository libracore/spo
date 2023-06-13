frappe.ui.form.on('Payment Reminder', {
    refresh: function(frm) {
        frm.add_custom_button(__("Erstelle Mahnungs-Sammel-PDF"), function() {
            
            frappe.call({
                method: 'spo.utils.print_mahnung.create_mahnungs_pdf',
                args: {
                    mahnung: cur_frm.doc.name
                },
                callback: function(r) {
                    cur_frm.reload_doc();
                    frappe.msgprint("Das PDF finden Sie im Anhang");
                }
            });
        });
    }
});
