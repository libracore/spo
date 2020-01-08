// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide('spo');

// add toolbar icon
$(document).bind('toolbar_setup', function() {
	frappe.app.name = "SPO";
	$('[data-link-type="forum"]').remove();
	$('[href="https://github.com/frappe/erpnext/issues"]').remove();
});



// preferred modules for breadcrumbs
$.extend(frappe.breadcrumbs.preferred, {
	"Customer": "SPO",
	"Sales Invoice": "SPO",
	"Address": "SPO",
	"Address And Contacts": "SPO"
});
