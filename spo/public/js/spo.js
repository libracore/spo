function fetch_data_from_search(frm, name) {
	frappe.call({
        "method": "spo.spo.doctype.anfrage.anfrage.update_frm_with_fetched_data",
        "args": {
            "frm": frm,
			"name": name
        },
        "async": false,
        "callback": function(response) {
           location.reload();
		   get_city_from_pincode(cur_frm.doc.plz, 'ort', 'kanton');
        }
    });
}