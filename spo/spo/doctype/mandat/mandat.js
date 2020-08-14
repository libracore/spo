// Copyright (c) 2019, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mandat', {
	refresh: function(frm) {
		/* //erstellen des Dashboards, wenn ein Mitglied eingetragen ist
		if (frm.doc.mitglied) {
			update_dashboard(frm);
		} */
		//erstellen des Dashboards
		update_dashboard(frm);
		
		// timer action icon
		cur_frm.page.add_action_icon(__("fa fa-history"), function() {
			timesheet_handling(frm);
		});
		
		//update timesheet table
		frappe.call({
			"method": "spo.spo.doctype.mandat.mandat.create_zeiten_uebersicht",
			"args": {
				"dt": cur_frm.doctype,
				"name": cur_frm.doc.name
			},
			"async": false,
			"callback": function(r) {
				if (r.message) {
					cur_frm.set_df_property('zeiten_uebersicht','options', r.message);
					$("[data-funktion='open_ts']").on('click', function() {
						console.log($(this).attr("data-referenz"));
						ts_bearbeiten($(this).attr("data-referenz"));
					});
				}
			}
		});
		
		set_adress_html_felder(frm);
		
		if (cur_frm.doc.anfragen) {
			frm.add_custom_button(__("Zurück zur Anfrage"), function() {
				frappe.set_route("Form", "Anfrage", cur_frm.doc.anfragen);
			});
		}
		
		frm.add_custom_button(__("Erteilen"), function() {
			master_freigabe_erteilen(frm);
		}, __("Master Freigabe für Mandat"));
		frm.add_custom_button(__("Entfernen"), function() {
			master_freigabe_entfernen(frm);
		}, __("Master Freigabe für Mandat"));
		frm.add_custom_button('Facharzt Bericht', function () {
			frm.trigger('get_facharzt');
		});
		
		cur_frm.fields_dict['kontakt'].get_query = function(doc) {
          return {
            filters: {
        	  "link_doctype": "Customer",
        	  "link_name": frm.doc.mitglied
            }
          }
        };
		cur_frm.fields_dict['adresse'].get_query = function(doc) {
          return {
            filters: {
        	  "link_doctype": "Customer",
        	  "link_name": frm.doc.mitglied
            }
          }
        };
	},
	absprung_einstellungen: function(frm) {
		frappe.set_route("Form", "Einstellungen");
	},
	get_facharzt: function (frm) {
		var d = new frappe.ui.Dialog({
			'fields': [
				{'fieldname': 'customer', 'fieldtype': 'Data', 'label': 'Facharzt'},
				{'fieldname': 'cb_1', 'fieldtype': 'Column Break'},
				{'fieldname': 'type', 'fieldtype': 'Link', 'options': 'Supplier Group', 'label': 'Type'},//, 'reqd': 1},
				{'fieldname': 'sb_1', 'fieldtype': 'Section Break'},
				{'fieldname': 'result', 'fieldtype': 'HTML'}
			],
			'title': __("Suchmaske Facharzt")
		});
		
		var $wrapper;
		var $results;
		var $placeholder;
		var $second_placeholder;
		var method = "spo.spo.doctype.mandat.mandat.get_facharzt_table";
		var columns = (["Link Name", "Facharzt", "Type"]);
		
		d.fields_dict["customer"].df.onchange = () => {
			var args = {
				customer: d.fields_dict.customer.input.value,
				type: d.fields_dict.type.input.value
			};
			get_facharzt_table(frm, $results, $placeholder, $second_placeholder, method, args, columns);
		}
		
		d.fields_dict["type"].df.onchange = () => {
			var args = {
				customer: d.fields_dict.customer.input.value,
				type: d.fields_dict.type.input.value
			};
			get_facharzt_table(frm, $results, $placeholder, $second_placeholder, method, args, columns);
		}
		
		$wrapper = d.fields_dict.result.$wrapper.append(`<div class="results"
			style="border: 1px solid #d1d8dd; border-radius: 3px; height: 300px; overflow: auto;"></div>`);
			
		$results = $wrapper.find('.results');
		
		$placeholder = $(`<div class="multiselect-empty-state">
					<span class="text-center" style="margin-top: -40px;">
						<i class="fa fa-2x fa-table text-extra-muted"></i>
						<p class="text-extra-muted">Kein Facharzt gefunden</p>
					</span>
				</div>`);
				
		$second_placeholder = $(`<div class="multiselect-empty-state">
					<span class="text-center" style="margin-top: -40px;">
						<i class="fa fa-2x fa-table text-extra-muted"></i>
						<p class="text-extra-muted">Bitte Type auswählen</p>
					</span>
				</div>`);
		
		$results.on('click', '.list-item--head :checkbox', (e) => {
			$results.find('.list-item-container .list-row-check')
				.prop("checked", ($(e.target).is(':checked')));
		});
		
		$results.empty();
		$results.append($placeholder);
		set_primary_action(frm, d, $results);
		
		var args = {
			customer: d.fields_dict.customer.input.value,
			type: d.fields_dict.type.input.value
		};
		
		get_facharzt_table(frm, $results, $placeholder, $second_placeholder, method, args, columns);
		d.show();
	}
});

var set_primary_action = function(frm, dialog, $results) {
	var me = this;
	dialog.set_primary_action(__('Weiter'), function() {
		let checked_value = get_checked_values($results);
		if(checked_value.length == 1){
			var facharzt = checked_value[0].reference;
			var mandat = cur_frm.doc.name;
			var customer_name = checked_value[0].facharzt;
			var customer_type = checked_value[0].customer_type;
			var confirm_dialog = new frappe.ui.Dialog({
				'fields': [
					{'fieldname': 'customer', 'fieldtype': 'Data', 'label': 'Ausgewählter Facharzt', 'default': customer_name, 'read_only': 1},
					{'fieldname': 'cb_1', 'fieldtype': 'Column Break'},
					{'fieldname': 'type', 'fieldtype': 'Data', 'label': 'Type', 'default': customer_type, 'read_only': 1},
					{'fieldname': 'sb_1', 'fieldtype': 'Section Break'},
					{'fieldname': 'create_new', 'fieldtype': 'Button', 'label': 'Neuer Bericht erstellen'},
					{'fieldname': 'cb_2', 'fieldtype': 'Column Break'},
					{'fieldname': 'read', 'fieldtype': 'Button', 'label': 'Bestehende(r) Bericht(e) öffnen'}
				],
				'title': __('Welche Aktion möchten Sie durchführen?')
			});
			confirm_dialog.fields_dict["create_new"].df.click = () => {
				confirm_dialog.hide();
				dialog.hide();
				create_facharzt_bericht(frm, mandat, facharzt);
			}
			
			confirm_dialog.fields_dict["read"].df.click = () => {
				confirm_dialog.hide();
				dialog.hide();
				show_facharzt_bericht_list(frm, mandat, facharzt);
			}
			
			confirm_dialog.show();
			
		} else if (checked_value.length > 1) {
			frappe.msgprint(__("Bitte selektieren Sie <b>nur</b> ein Facharzt"));
		} else {
			frappe.msgprint(__("Bitte selektieren Sie einen Facharzt"));
		}
	});
};

var get_facharzt_table = function(frm, $results, $placeholder, $second_placeholder, method, args, columns) {
	var me = this;
	$results.empty();
	//if (args.type) {
		frappe.call({
			method: method,
			args: args,
			callback: function(data) {
				if(data.message){
					$results.append(make_list_row(columns));
					for(let i=0; i<data.message.length; i++){
						$results.append(make_list_row(columns, data.message[i]));
					}
				} else {
					$results.append($placeholder);
				}
			}
		});
	/* } else {
		$results.append($second_placeholder);
	} */
}

var make_list_row= function(columns, result={}) {
	var me = this;
	// Make a head row by default (if result not passed)
	let head = Object.keys(result).length === 0;
	let contents = ``;
	columns.forEach(function(column) {
		var column_value = '-';
		if (result[column]) {
			column_value = result[column];
		}
		contents += `<div class="list-item__content ellipsis">
			${
				head ? `<span class="ellipsis">${__(frappe.model.unscrub(column))}</span>`
				:(column !== "name" ? `<span class="ellipsis">${__(column_value)}</span>`
					: `<a class="list-id ellipsis">
						${__(result[column])}</a>`)
			}
		</div>`;
	})

	let $row = $(`<div class="list-item">
		<div class="list-item__content" style="flex: 0 0 10px;">
			<input type="checkbox" class="list-row-check" ${result.checked ? 'checked' : ''}>
		</div>
		${contents}
	</div>`);

	$row = list_row_data_items(head, $row, result);
	return $row;
};

var list_row_data_items = function(head, $row, result) {
	head ? $row.addClass('list-item--head')
		: $row = $(`<div class="list-item-container"
			data-reference= "${result.reference}"
			data-customername = "${result.Facharzt}"
			data-customertype = "${result.Type}">
			</div>`).append($row);
	return $row
};

var get_checked_values= function($results) {
	return $results.find('.list-item-container').map(function() {
		let checked_values = {};
		if ($(this).find('.list-row-check:checkbox:checked').length > 0 ) {
			checked_values['reference'] = $(this).attr('data-reference');
			checked_values['facharzt'] = $(this).attr('data-customername');
			checked_values['customer_type'] = $(this).attr('data-customertype');
			return checked_values
		}
	}).get();
};

function update_dashboard(frm) {
	frappe.call({
		"method": "spo.spo.doctype.mandat.mandat.get_dashboard_data",
		"args": {
			"mitglied": frm.doc.mitglied,
			"anfrage": frm.doc.anfragen,
			"mandat": frm.doc.name
		},
		"async": false,
		"callback": function(response) {
			var query = response.message;
			var max_aufwand = query.callcenter_limit;
			if (frm.doc.max_aufwand > 0) {
				max_aufwand = frm.doc.max_aufwand;
			}
			//Limits
			var _colors = ['#d40000', '#00b000'];
			var aufwand_in_ch = query.callcenter_verwendet;
			if (aufwand_in_ch == 0) {
				_colors = ['#00b000', '#d40000'];
			} else {
				aufwand_in_ch = (aufwand_in_ch / 60) * frm.doc.stundensatz;
			}
			let limit_chart = new frappe.Chart( "#limit", { // or DOM element
				data: {
				labels: [__("Verwendet"), __("Ausstehend")],

				datasets: [
					{
						values: [aufwand_in_ch, max_aufwand - aufwand_in_ch]
					}
				],

				},
				title: __("Auswertung Kostendach (in CHF)"),
				type: 'percentage', // or 'bar', 'line', 'pie', 'percentage'
				colors: _colors,
				barOptions: {
					height: 20,          // default: 20
					depth: 2             // default: 2
				}
			});
		}
	});
}


function timesheet_handling(frm) {
	frappe.prompt([
		{'fieldname': 'datum', 'fieldtype': 'Date', 'label': 'Datum', 'reqd': 1, 'default': 'Today'},
		{'fieldname': 'arbeit', 'fieldtype': 'Select', 'label': __('Arbeitsinhalt'), 'reqd': 1, options: [__('Korrespondenz'), __('Telefonat'), __('Aktenstudium'), __('Organisation der juristischen Beratung'), __('Juristische Beratung'), __('Recherche Facharzt'), __('Organisation Facharzt'), __('Interne fachliche Besprechung'), __('Sonstiges')]},
		{'fieldname': 'remark', 'fieldtype': 'Small Text', 'label': __('Bemerkung'), 'reqd': 0},
		{'fieldname': 'time', 'fieldtype': 'Float', 'label': 'Arbeitszeit (in h)', 'reqd': 1}  
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
				"bemerkung": values.arbeit + ": " + (values.remark||'')
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

function ts_bearbeiten(ts) {
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

function set_kunden_html(frm) {
	if (cur_frm.doc.customer && cur_frm.doc.kontakt && cur_frm.doc.adresse) {
		frappe.call({
			"method": "spo.spo.doctype.anfrage.anfrage.get_kunden_data",
			"args": {
				"kunde": cur_frm.doc.customer,
				"adresse": cur_frm.doc.adresse,
				"kontakt": cur_frm.doc.kontakt
			},
			"async": false,
			"callback": function(r) {
				cur_frm.set_df_property('kunde_html','options', r.message);
				cur_frm.set_df_property('kunden_dashboard_html','options', r.message);
			}
		});
	}
}

function set_angehoerige_html(frm) {
	if (cur_frm.doc.ang && cur_frm.doc.ang_adresse && cur_frm.doc.ang_kontakt) {
		frappe.call({
			"method": "spo.spo.doctype.anfrage.anfrage.get_angehoerige_data",
			"args": {
				"ang": cur_frm.doc.ang,
				"adresse": cur_frm.doc.ang_adresse,
				"kontakt": cur_frm.doc.ang_kontakt
			},
			"async": false,
			"callback": function(r) {
				cur_frm.set_df_property('ang_html','options', r.message);
			}
		});
	}
}

function set_rsv_html(frm) {
	if (cur_frm.doc.rsv && cur_frm.doc.rsv_adresse && cur_frm.doc.rsv_kontakt) {
		frappe.call({
			"method": "spo.spo.doctype.anfrage.anfrage.get_rsv_data",
			"args": {
				"rsv": cur_frm.doc.rsv,
				"adresse": cur_frm.doc.rsv_adresse,
				"kontakt": cur_frm.doc.rsv_kontakt
			},
			"async": false,
			"callback": function(r) {
				cur_frm.set_df_property('rsv_html','options', r.message);
			}
		});
	}
}


function set_adress_html_felder(frm) {
	set_kunden_html(frm);
	set_angehoerige_html(frm);
	set_rsv_html(frm);
}

function master_freigabe_erteilen(frm) {
	frappe.prompt([
		{'fieldname': 'user', 'fieldtype': 'Link', 'label': 'Benutzer', 'reqd': 1, 'options': 'User'}  
	],
	function(values){
		frappe.call({
			"method": "spo.spo.doctype.mandat.mandat.share_mandat_and_related_docs",
			"args": {
				"mandat": cur_frm.doc.name,
				"user_to_add": values.user
			},
			"async": false,
			"callback": function(r) {
				if (r.message=='ok') {
					cur_frm.reload_doc();
				}
			}
		});
	},
	'Master Freigabe erteilen',
	'Erteilen'
	);
}

function master_freigabe_entfernen(frm) {
	frappe.prompt([
		{'fieldname': 'user', 'fieldtype': 'Link', 'label': 'Benutzer', 'reqd': 1, 'options': 'User'}  
	],
	function(values){
		frappe.call({
			"method": "spo.spo.doctype.mandat.mandat.remove_share_of_mandat_and_related_docs",
			"args": {
				"mandat": cur_frm.doc.name,
				"user_to_remove": values.user
			},
			"async": false,
			"callback": function(r) {
				if (r.message=='ok') {
					cur_frm.reload_doc();
				}
			}
		});
	},
	'Master Freigabe entfernen',
	'Entfernen'
	);
}

function create_facharzt_bericht(frm, mandat, facharzt) {
	frappe.call({
		method: 'spo.spo.doctype.mandat.mandat.create_new_facharzt_bericht',
		args: {
			'mandat': mandat,
			'facharzt': facharzt
		},
		callback: function(r) {
			if(r.message) {
				frappe.set_route("Form", "Facharzt Bericht", r.message)
			} 
		}
	});
}

function show_facharzt_bericht_list(frm, mandat, facharzt) {
	frappe.route_options = {"mandat": ["=", mandat], 'facharzt': ["=", facharzt]};
	frappe.set_route("List", "Facharzt Bericht");
}