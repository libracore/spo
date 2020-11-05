cur_frm.dashboard.add_transactions([
	{
		'label': 'SPO Referenzen',
		'items': [
			'Anfrage',
			'Mandat',
			'Mitgliedschaft',
			'Freies Schreiben'
		]
	}
]);

frappe.ui.form.on('Customer', {
	refresh: function(frm) {
		frappe.call({
			method: 'spo.scripts.custom_scripts.customer.get_spenden',
			args: {
				customer: cur_frm.doc.name
			},
			callback: function(r) {
				if(r.message) {
					var spenden_html = '<h3>Spendenübersicht</h3><div class="row"><div class="col-xs-6">Aktuelles Jahr:<br>CHF ' + parseFloat(r.message.aktuell) + '</div><div class="col-xs-6">Letzte 5 Jahre:<br>CHF ' + parseFloat(r.message.total) + '</div></div>';
					cur_frm.dashboard.add_section(spenden_html);
				} 
			}
		});
	}
});