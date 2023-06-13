frappe.listview_settings['Payment Reminder'] = {
    onload: function(listview) {
        listview.page.add_menu_item( __("Create Payment Reminders"), function() {
            frappe.prompt(
                [
                    {'fieldname': 'company', 'fieldtype': 'Link', 'options': 'Company', 'label': __('Company'), 'reqd': 1, 'default': frappe.defaults.get_user_default('company')}
                ],
                function(values){
                    create_payment_reminders(values);
                },
                __("Create Payment Reminders"),
                __("Create")
            );
        });  
        listview.page.add_menu_item( __("Erstelle Mahnungs-Sammel-PDF"), function() {
            print_pdf();
        });
    }
}

function create_payment_reminders(values) {
    frappe.call({
        'method': "erpnextswiss.erpnextswiss.doctype.payment_reminder.payment_reminder.create_payment_reminders",
        'args': {
            'company': values.company
        },
        'callback': function(response) {
            frappe.show_alert( __("Payment Reminders created") );
        }
    });
}

function print_pdf() {
    console.log(cur_list.get_checked_items());
    var loop = 0;
    var mahnungen = [];
    cur_list.$freeze.toggle();
    cur_list.$freeze.html("Bitte warten, PDFs werden erzeugt...")
    cur_list.get_checked_items().forEach(function(entry){
        mahnungen.push(entry.name);
    });
    var kwargs = {
        'mahnungen': mahnungen
    }
    frappe.call({
        method: 'spo.utils.print_mahnung.multi_print_bind',
        args: {
            kwargs: kwargs
        },
        callback: function(r) {
            cur_list.$freeze.toggle();
            window.open('https://spo.libracore.ch' + r.message,'_blank');
        }
    });
}
