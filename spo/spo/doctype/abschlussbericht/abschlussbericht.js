// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Abschlussbericht', {
	refresh: function(frm) {
		// filter for textbaustein based on doctype and user
		cur_frm.fields_dict['textkonserve'].get_query = function(doc) {
			 return {
				 filters: {
					 "mitarbeiter": frappe.user.name,
					 "dokument": "Abschlussbericht"
				 }
			 }
		}
	}
});
