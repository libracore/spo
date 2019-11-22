frappe.ui.form.on('Address', {
	validate: function(frm) {
		if (cur_frm.doc.plz != cur_frm.doc.pincode) {
			cur_frm.set_value('pincode', cur_frm.doc.plz);
		}
	},
	plz: function(frm) {
		get_city_from_pincode(cur_frm.doc.plz, 'city', 'kanton');
	}
});