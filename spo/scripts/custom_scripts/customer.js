frappe.ui.form.on('Customer', {
	refresh: function(frm) {
		if (!frm.doc.__islocal) {
			check_contact(frm);
			
			//add btn to create Membership
			frm.add_custom_button(__("Membership"), function(frm) {
				frappe.call({
					method: "spo.scripts.custom_scripts.customer.create_mitgliedschaft",
					args:{
						"customer": cur_frm.doc.name
					},
					callback: function(r)
					{
						frappe.set_route("Form", "Mitgliedschaft", r.message);
					}
				});
			}, __("Make"));
			
			//add btn to create anfrage
			frm.add_custom_button(__("Anfrage"), function(frm) {
				frappe.call({
					method: "spo.scripts.custom_scripts.customer.create_anfrage",
					args:{
						"customer": cur_frm.doc.name
					},
					callback: function(r)
					{
						frappe.set_route("Form", "Anfrage", r.message);
					}
				});
			}, __("Make"));
			
			//add btn to create mandat
			frm.add_custom_button(__("Mandat"), function() {
				frappe.call({
					method: "spo.scripts.custom_scripts.customer.create_mandat",
					args:{
						"customer": cur_frm.doc.name
					},
					callback: function(r)
					{
						frappe.set_route("Form", "Mandat", r.message);
					}
				});
			}, __("Make"));
			
			//add btn to show Membership
			frm.add_custom_button(__("Membership"), function(frm) {
				frappe.route_options = {"mitglied": ["like", "%" + cur_frm.doc.name + "%"]};
				frappe.set_route("List", "Mitgliedschaft");
			}, __("Show"));
			
			//add btn to show anfrage
			frm.add_custom_button(__("Anfrage"), function() {
				frappe.route_options = {"mitglied": ["like", "%" + cur_frm.doc.name + "%"]};
				frappe.set_route("List", "Anfrage");
			}, __("Show"));
			
			//add btn to Show mandat
			frm.add_custom_button(__("Mandat"), function() {
				frappe.route_options = {"mitglied": ["like", "%" + cur_frm.doc.name + "%"]};
				frappe.set_route("List", "Mandat");
			}, __("Show"));
		}
	}
});

function check_contact(frm) {
	frappe.call({
		method: 'spo.scripts.custom_scripts.customer.check_contact',
		args: {
			'customer': frm.doc.name
		},
		callback: function(r) {}
	});
}