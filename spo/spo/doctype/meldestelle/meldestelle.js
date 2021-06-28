// Copyright (c) 2021, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Meldestelle', {
	refresh: function(frm) {
        // timer action icon
		cur_frm.page.add_action_icon(__("fa fa-history"), function() {
			timesheet_handling(frm);
		});
        
        update_timesheet_table(frm);
        
        // set filters
        cur_frm.fields_dict['contact'].get_query = function(doc) {
             return {
                filters: {
                    "link_doctype": "Customer",
                    "link_name": cur_frm.doc.customer
                }
             }
        };
        cur_frm.fields_dict['address'].get_query = function(doc) {
             return {
                 filters: {
                    "link_doctype": "Customer",
                    "link_name": cur_frm.doc.customer
                }
             }
        };
        
        // freeze on status = completed
        check_status(frm);
	},
    customer: function(frm) {
        cur_frm.set_value("contact", null);
        cur_frm.set_value("address", null);
    },
    status: function(frm) {
        check_status(frm);
    }
});

function timesheet_handling(frm) {
	frappe.prompt([
		{'fieldname': 'datum', 'fieldtype': 'Date', 'label': 'Datum', 'reqd': 1, 'default': 'Today'},
		{'fieldname': 'time', 'fieldtype': 'Float', 'label': 'Arbeitszeit (in h)', 'reqd': 1},
		{'fieldname': 'remark', 'fieldtype': 'Small Text', 'label': __('Bemerkung'), 'reqd': 0}
	],
	function(values){
		frappe.call({
			"method": "spo.utils.timesheet_handlings.create_ts_entry",
			"args": {
				"user": frappe.session.user_email,
				"doctype": frm.doc.doctype,
				"record": frm.doc.name,
				"time": values.time,
				"datum": values.datum,
				"bemerkung": (values.remark||'')
			},
			"async": false,
			"callback": function(response) {
				//done
			}
		});
	},
	__('Arbeitszeit erfassen'),
	__('Erfassen')
	)
}

function update_timesheet_table(frm) {
    frappe.call({
        "method": "spo.spo.doctype.mandat.mandat.create_zeiten_uebersicht",
        "args": {
            "dt": cur_frm.doctype,
            "name": cur_frm.doc.name
        },
        "async": false,
        "callback": function(r) {
            if (r.message) {
                cur_frm.set_df_property('timelogs','options', r.message);
                $("[data-funktion='open_ts']").on('click', function() {
                    edit_ts($(this).attr("data-referenz"));
                });
            }
        }
    });
}

function edit_ts(ts) {
	frappe.call({
		"method": "spo.utils.timesheet_handlings.check_ts_owner",
		"args": {
			"ts": ts,
			"user": frappe.session.user_email
		},
		"async": false,
		"callback": function(r) {
			if (r.message) {
				frappe.route_options = {"timesheet": ts};
				frappe.set_route("Form", "Zeiterfassung");
			} else {
				frappe.msgprint(__("Sie können nur Ihre eigene Timesheets bearbeiten."), __("Nicht Ihr Timesheet"));
			}
		}
	});
}

function check_status(frm) {
    if (cur_frm.doc.status == 'Completed') {
        cur_frm.set_df_property('applicant_name','read_only', 1);
        cur_frm.set_df_property('contact_number','read_only', 1);
        cur_frm.set_df_property('contact_mail','read_only', 1);
        cur_frm.set_df_property('from_time','read_only', 1);
        cur_frm.set_df_property('to_time','read_only', 1);
        cur_frm.set_df_property('topic','read_only', 1);
        cur_frm.set_df_property('message','read_only', 1);
        cur_frm.set_df_property('customer','read_only', 1);
        cur_frm.set_df_property('contact','read_only', 1);
        cur_frm.set_df_property('address','read_only', 1);
    } else {
        cur_frm.set_df_property('applicant_name','read_only', 0);
        cur_frm.set_df_property('contact_number','read_only', 0);
        cur_frm.set_df_property('contact_mail','read_only', 0);
        cur_frm.set_df_property('from_time','read_only', 0);
        cur_frm.set_df_property('to_time','read_only', 0);
        cur_frm.set_df_property('topic','read_only', 0);
        cur_frm.set_df_property('message','read_only', 0);
        cur_frm.set_df_property('customer','read_only', 0);
        cur_frm.set_df_property('contact','read_only', 0);
        cur_frm.set_df_property('address','read_only', 0);
    }
}
