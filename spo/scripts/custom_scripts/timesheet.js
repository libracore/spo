frappe.ui.form.on('Timesheet', {
	onload: function (frm) {
		// restrict Dynamic Links to SPO
		frm.set_query('spo_dokument', 'time_logs', function () {
			return {
				'filters': {
					'module': 'SPO',
					'istable': 0,
				}
			};
		});
	}
})