frappe.ui.form.on('Holiday List', {
	add_sick_days_to_holiday: function(frm) {
		if (cur_frm.doc.from_date_sick && cur_frm.doc.to_date_sick) {
			var from_date = cur_frm.doc.from_date_sick;
			var to_date = cur_frm.doc.to_date_sick;
			var day_diff = frappe.datetime.get_day_diff(cur_frm.doc.to_date_sick, cur_frm.doc.from_date_sick);
			var i;
			for (i=0; i <= day_diff; i++) {
				var child = cur_frm.add_child('holidays');
				frappe.model.set_value(child.doctype, child.name, 'holiday_date', from_date);
				frappe.model.set_value(child.doctype, child.name, 'description', "Krank");
				cur_frm.refresh_field('holidays');
				from_date = frappe.datetime.add_days(from_date, 1);
			}
			cur_frm.set_value('from_date_sick', '');
			cur_frm.set_value('to_date_sick', '');			
		} else {
			frappe.msgprint("Bitte wählen Sie zuerst ein Von und ein Bis Datum aus.");
		}
	}
});