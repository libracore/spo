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
        }
    });
}

document.onreadystatechange = () => {
	if (document.readyState === 'complete') {
		if (window.location.href.indexOf("/desk#Form/Anfrage/" > -1)) {
			setTimeout(function() {
				document.getElementsByClassName("section-head")[1].click();
			}, 2000);
		}
	}
};
