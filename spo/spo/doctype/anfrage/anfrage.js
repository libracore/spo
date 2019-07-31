// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Anfrage', {
	refresh: function(frm) {
		//add btn to create Mandat
		frm.add_custom_button(__("Convert to Mandat"), function() {
            new_mandat(frm.doc.name);
        });
	}
});

function new_mandat(anfrage) {
	frappe.call({
		method: 'spo.scripts.mandat.creat_new_mandat',
		args: {
			'anfrage': anfrage
		},
		callback: function(r) {
			if(r.message) {
				if (r.message != 'already exist') {
					frappe.set_route("Form", "Mandat", r.message)
				} else {
					frappe.confirm(
						'Zu dieser Anfrage wurde bereits ein Mandat eröffnet.<br><br>Soll das/die Mandat(e) angezeigt werden?',
						function(){
							// on yes
							show_mandat_list_based_on_anfrage();
						},
						function(){
							// on no
						}
					);
				}
			} 
		}
	});
}

function show_mandat_list_based_on_anfrage() {
	frappe.route_options = {"anfragen": ["like", "%" + cur_frm.doc.name + "%"]};
	frappe.set_route("List", "Mandat");
}