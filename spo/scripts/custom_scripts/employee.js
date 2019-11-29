frappe.ui.form.on('Employee', {
	validate: function(frm) {
		calc_monatslohn(frm);	
	},
	monatslohn: function(frm) {
		calc_monatslohn(frm);	
	},
	anstellungsgrad: function(frm) {
		calc_monatslohn(frm);	
	}
});

function calc_monatslohn(frm) {
	if (cur_frm.doc.anstellung == 'Festanstellung') {
		var monatslohn = (cur_frm.doc.monatslohn / 100) * cur_frm.doc.anstellungsgrad;
		if (cur_frm.doc.brutto_monatslohn != monatslohn) {
			cur_frm.set_value('brutto_monatslohn', monatslohn);
		}
	}
}