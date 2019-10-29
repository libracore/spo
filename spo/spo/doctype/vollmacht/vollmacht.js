// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vollmacht', {
	before_save: function(frm) {
		if (!cur_frm.doc.titelzeile && !cur_frm.doc.todesfall) {
			var titelzeile_string = '<p><b>Abklärungen im Zusammenhang mit</b> (dem Eingriffes/ der Operation) <b>vom</b> (Datum)  <b>im Spital XY</b> (Ort) <b>samt</b> (Folgen) oder (inkl. Vor- und Nachbehandlung)<b>.</b></p>';
			cur_frm.set_value('titelzeile', titelzeile_string);
		} else if (!cur_frm.doc.titelzeile && cur_frm.doc.todesfall) {
			var titelzeile_string = '<p><b>Abklärung der medizinischen Behandlung vom</b> (Datum) <b>im Spital XY</b> (Ort) <b>samt Folgen im Zusammenhang mit dem Todesfall betreffend Herrn/Frau/des Kindes</b> (fett: † Name, geb*   – gest., Adresse) <b>insbesondere vollständige Einsicht in die damit verbundenen Akten.</b></p>';
			cur_frm.set_value('titelzeile', titelzeile_string);
		}
	},
	validate: function(frm) {
		frappe.prompt([
			{'fieldname': 'time', 'fieldtype': 'Float', 'label': 'Total Time (in hours)', 'reqd': 1}  
		],
		function(values){
			console.log(frm.doc.doctype);
			frappe.call({
				"method": "spo.utils.timesheet_handlings.handle_timesheet",
				"args": {
					"user": frappe.session.user_email,
					"doctype": frm.doc.doctype,
					"reference": frm.doc.name,
					"time": values.time
				},
				"async": false,
				"callback": function(response) {
					console.log(response);
				}
			});
		},
		'Timesheet Action',
		'Go'
		)
	},
	refresh: function(frm) {
		if (cur_frm.doc.mandat) {
			frappe.call({
				"method": "frappe.client.get",
				"args": {
					"doctype": "Mandat",
					"name": frm.doc.mandat
				},
				"callback": function(response) {
					var mandat = response.message;

					if (mandat) {
						frappe.call({
							"method": "frappe.client.get",
							"args": {
								"doctype": "Customer",
								"name": mandat.mitglied
							},
							"callback": function(response) {
								var mitglied = response.message;

								if (mitglied) {
									if (!cur_frm.doc.name_vorname) {
										cur_frm.set_value('name_vorname', mitglied.customer_name);
									}
									if (!cur_frm.doc.adresse) {
										frappe.call({
											method:"frappe.client.get_list",
											args:{
												doctype:"Dynamic Link",
												filters: [
													["link_doctype","=", 'Customer'],
													["link_name","=", mitglied.name],
													["parenttype","=", 'Address']
												],
												fields: ["parent"],
												parent: "Address"
											},
											callback: function(r) {
												if (r.message) {
													var adress_link = r.message[0].parent;
													if (adress_link) {
														frappe.call({
															"method": "frappe.client.get",
															"args": {
																"doctype": "Address",
																"name": adress_link
															},
															"callback": function(response) {
																var address = response.message;
																if (address) {
																	cur_frm.set_value('adresse', address.address_line1);
																}
															}
														});
													}
												}
											}
										});
									}
									if (!cur_frm.doc.email) {
										frappe.call({
											method:"frappe.client.get_list",
											args:{
												doctype:"Dynamic Link",
												filters: [
													["link_doctype","=", 'Customer'],
													["link_name","=", mitglied.name],
													["parenttype","=", 'Contact']
												],
												fields: ["parent"],
												parent: "Contact"
											},
											callback: function(r) {
												if (r.message) {
													var contact_link = r.message[0].parent;
													if (contact_link) {
														frappe.call({
															"method": "frappe.client.get",
															"args": {
																"doctype": "Contact",
																"name": contact_link
															},
															"callback": function(response) {
																var contact = response.message;
																if (contact) {
																	cur_frm.set_value('email', contact.email_id);
																	if (!cur_frm.doc.telefon) {
																		cur_frm.set_value('telefon', contact.phone);
																	}
																	if (!cur_frm.doc.geburtsdatum) {
																		cur_frm.set_value('geburtsdatum', contact.geburtsdatum);
																	}
																}
															}
														});
													}
												}
											}
										});
									}
								}
							}
						});
					}
				}
			});
		}
		if (!cur_frm.doc.berater) {
			cur_frm.set_value('berater', frappe.user_info().fullname);
		}
		
		// filter for textbaustein (titelzeile) based on doctype and user
		cur_frm.fields_dict['textkonserve'].get_query = function(doc) {
			 return {
				 filters: {
					 "mitarbeiter": frappe.user.name,
					 "dokument": "Vollmacht - Titelzeile"
				 }
			 }
		}
		
		// filter for textbaustein (begleitbrief) based on doctype and user
		cur_frm.fields_dict['textkonserve'].get_query = function(doc) {
			 return {
				 filters: {
					 "mitarbeiter": frappe.user.name,
					 "dokument": "Vollmacht - Begleitbrief"
				 }
			 }
		}
	}
});
