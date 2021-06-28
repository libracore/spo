frappe.listview_settings['Meldestelle'] = {
	add_fields: ["status"],
	get_indicator: function(doc) {
		if (doc.status== "Created") {
			return [__("Created"), "red", "status,=," + "Created"]
		}
		
		if (doc.status== "In progress") {
			return [__("In progress"), "orange", "status,=," + "In progress"]
		}
		
		if (doc.status== "To be charged") {
			return [__("To be charged"), "yellow", "status,=," + "To be charged"]
		}
		
		if (doc.status== "Completed") {
			return [__("Completed"), "green", "status,=," + "Completed"]
		}
	}
};
