// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Anfrage', {
	refresh: function(frm) {
		//add btn to create Mandat
		frm.add_custom_button(__("Convert to Mandat"), function() {
            new_mandat(frm.doc.name);
        });
		//var import_mitgliederdaten_btn = frm.fields_dict.import_mitgliederdaten.input //.addEventListener("click", function(frm) { console.log("yess duuuu"); } );
		//console.log(import_mitgliederdaten_btn);
		//import_mitgliederdaten_btn.addEventListener("click", function(frm) { console.log("yess duuuu"); } );
	},
	import_mitgliederdaten: function(frm) {
		if (frm.doc.mitglied) {
			// do some stuff
		} else {
			frappe.prompt([
				{'fieldname': 'mitgliedernummer', 'fieldtype': 'Link', 'label': 'Mitglied', 'reqd': 1, 'options': 'Customer'}  
			],
			function(values){
				cur_frm.set_value('mitglied', values.mitgliedernummer);
				// do some stuff
			},
			'Bitte geben Sie die Mitgliedernummer an',
			'Daten importieren'
			);
		}
	},
	mitglied_erstellen: function(frm) {
		frappe.msgprint("Muss noch programmiert werden....");
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
	frappe.set_route("List", "Mandat");4 
}