// Copyright (c) 2021, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Beratungsplanung', {
    button_set_slots: function(frm) {
        slot_dialog(frm);
    }
});

function fill_date(frm, options) {
    var year = frm.doc.year;
    var month = frm.doc.month;
    //get nr of days in this month
    var daysInMonth = new Date(year, month, 0).getDate();

    //delete old values: remove all rows
    var tbl = frm.doc.sloteingaben || [];
    var i = tbl.length;
    while (i--)
    {
        cur_frm.get_field("sloteingaben").grid.grid_rows[i].remove();
    }
    cur_frm.refresh();
    
    //loop, day starts at 1
    for (var day = 1; day <= daysInMonth; day++) {
        //fill in sloteingaben (childtbl)
        //month starts at 0
        var date = new Date(year, month-1, day);
        var dayOfWeek = date.getDay();      // 0 = Sunday, 1 = Monday, ... 6 = Saturday
        if ((dayOfWeek > 0) && (dayOfWeek < 6)) {
            // only process for weekdays
            var topic = null;
            var user = null;
            var time = null;
            var create = false;
            // check if this day is required - Monday
            if ((dayOfWeek === 1) && (options.med_mon_mor === 1)) {
                topic = "Medizin";
                user = options.advisor_mon_mor;
                time = "10+11";
                create = true;
            } else if ((dayOfWeek === 1) && (options.med_mon_aft === 1)) {
                topic = "Medizin";
                user = options.advisor_mon_aft;
                time = "14+15";
                create = true;
            }
            if ((dayOfWeek === 1) && (options.dent_mon_mor === 1)) {
                topic = "Zahnmedizin";
                user = options.advisor_mon_mor;
                time = "10+11";
                create = true;
            } else if ((dayOfWeek === 1) && (options.dent_mon_aft === 1)) {
                topic = "Zahnmedizin";
                user = options.advisor_mon_aft;
                time = "14+15";
                create = true;
            }
            //Tuesday
            if ((dayOfWeek === 2) && (options.med_tue_mor === 1)) {
                topic = "Medizin";
                user = options.advisor_tue_mor;
                time = "10+11";
                create = true;
            } else if ((dayOfWeek === 2) && (options.med_tue_aft === 1)) {
                topic = "Medizin";
                user = options.advisor_tue_aft;
                time = "14+15";
                create = true;
            }
            if ((dayOfWeek === 2) && (options.dent_tue_mor === 1)) {
                topic = "Zahnmedizin";
                user = options.advisor_tue_mor;
                time = "10+11";
                create = true;
            } else if ((dayOfWeek === 2) && (options.dent_tue_aft === 1)) {
                topic = "Zahnmedizin";
                user = options.advisor_tue_aft;
                time = "14+15";
                create = true;
            }
            //Wednesday
            if ((dayOfWeek === 3) && (options.med_wed_mor === 1)) {
                topic = "Medizin";
                user = options.advisor_wed_mor;
                time = "10+11";
                create = true;
            } else if ((dayOfWeek === 3) && (options.med_wed_aft === 1)) {
                topic = "Medizin";
                user = options.advisor_wed_aft;
                time = "14+15";
                create = true;
            }
            if ((dayOfWeek === 3) && (options.dent_wed_mor === 1)) {
                topic = "Zahnmedizin";
                user = options.advisor_wed_mor;
                time = "10+11";
                create = true;
            } else if ((dayOfWeek === 3) && (options.dent_wed_aft === 1)) {
                topic = "Zahnmedizin";
                user = options.advisor_wed_aft;
                time = "14+15";
                create = true;
            }
            //Thursday
            if ((dayOfWeek === 4) && (options.med_thu_mor === 1)) {
                topic = "Medizin";
                user = options.advisor_thu_mor;
                time = "10+11";
                create = true;
            } else if ((dayOfWeek === 34) && (options.med_thu_aft === 1)) {
                topic = "Medizin";
                user = options.advisor_thu_aft;
                time = "14+15";
                create = true;
            }
            if ((dayOfWeek === 4) && (options.dent_thu_mor === 1)) {
                topic = "Zahnmedizin";
                user = options.advisor_thu_mor;
                time = "10+11";
                create = true;
            } else if ((dayOfWeek === 4) && (options.dent_thu_aft === 1)) {
                topic = "Zahnmedizin";
                user = options.advisor_thu_aft;
                time = "14+15";
                create = true;
            }
            //Friday
            if ((dayOfWeek === 5) && (options.med_fri_mor === 1)) {
                topic = "Medizin";
                user = options.advisor_fri_mor;
                time = "10+11";
                create = true;
            } else if ((dayOfWeek === 5) && (options.med_fri_aft === 1)) {
                topic = "Medizin";
                user = options.advisor_fri_aft;
                time = "14+15";
                create = true;
            }
            if ((dayOfWeek === 5) && (options.dent_fri_mor === 1)) {
                topic = "Zahnmedizin";
                user = options.advisor_fri_mor;
                time = "10+11";
                create = true;
            } else if ((dayOfWeek === 5) && (options.dent_fri_aft === 1)) {
                topic = "Zahnmedizin";
                user = options.advisor_wed_aft;
                time = "14+15";
                create = true;
            }
            if (create) {
                var child = cur_frm.add_child('sloteingaben');
                // set weekday corresponding to options of Sloteingabe Details
                var weekdays = ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"];

                frappe.model.set_value(child.doctype, child.name, 'weekday', weekdays[dayOfWeek]);
                frappe.model.set_value(child.doctype, child.name, 'date', date.toISOString().substr(0,10));
                frappe.model.set_value(child.doctype, child.name, 'objective', topic);
                frappe.model.set_value(child.doctype, child.name, 'time', time);
                frappe.model.set_value(child.doctype, child.name, 'user', user);
            }
        }
    }
    cur_frm.refresh_field('sloteingaben');
}

function slot_dialog(frm) {
    var dialog = new frappe.ui.Dialog({
      'title': __('Welche Slots möchten Sie erstellen?'),
      'fields': [
        {'fieldname': 'med_mon_mor', 'fieldtype': 'Check', 'label': __('Medizin Mo Vormittag')},
        {'fieldname': 'med_mon_aft', 'fieldtype': 'Check', 'label': __('Medizin Mo Nachmittag')},
        {'fieldname': 'med_tue_mor', 'fieldtype': 'Check', 'label': __('Medizin Di Vormittag')},
        {'fieldname': 'med_tue_aft', 'fieldtype': 'Check', 'label': __('Medizin Di Nachmittag')},
        {'fieldname': 'med_wed_mor', 'fieldtype': 'Check', 'label': __('Medizin Mi Vormittag')},
        {'fieldname': 'med_wed_aft', 'fieldtype': 'Check', 'label': __('Medizin Mi Nachmittag')},
        {'fieldname': 'med_thu_mo', 'fieldtype': 'Check', 'label': __('Medizin Do Vormittag')},
        {'fieldname': 'med_thu_aft', 'fieldtype': 'Check', 'label': __('Medizin Do Nachmittag')},
        {'fieldname': 'med_fri_mor', 'fieldtype': 'Check', 'label': __('Medizin Fr Vormittag')},
        {'fieldname': 'med_fri_aft', 'fieldtype': 'Check', 'label': __('Medizin Fr Nachmittag')},
        {'fieldname': 'col1', 'fieldtype': 'Column Break'},
        {'fieldname': 'dent_mon_mor', 'fieldtype': 'Check', 'label': __('Zahnmedizin Mo Vormittag')},
        {'fieldname': 'dent_mon_aft', 'fieldtype': 'Check', 'label': __('Zahnmedizin Mo Nachmittag')},
        {'fieldname': 'dent_tue_mor', 'fieldtype': 'Check', 'label': __('Zahnmedizin Di Vormittag')},
        {'fieldname': 'dent_tue_aft', 'fieldtype': 'Check', 'label': __('Zahnmedizin Di Nachmittag')},
        {'fieldname': 'dent_wed_mor', 'fieldtype': 'Check', 'label': __('Zahnmedizin Mi Vormittag')},
        {'fieldname': 'dent_wed_aft', 'fieldtype': 'Check', 'label': __('Zahnmedizin Mi Nachmittag')},
        {'fieldname': 'dent_thu_mo', 'fieldtype': 'Check', 'label': __('Zahnmedizin Do Vormittag')},
        {'fieldname': 'dent_thu_aft', 'fieldtype': 'Check', 'label': __('Zahnmedizin Do Nachmittag')},
        {'fieldname': 'dent_fri_mor', 'fieldtype': 'Check', 'label': __('Zahnmedizin Fr Vormittag')},
        {'fieldname': 'dent_fri_aft', 'fieldtype': 'Check', 'label': __('Zahnmedizin Fr Nachmittag')},
        {'fieldname': 'col2', 'fieldtype': 'Column Break'},
        {'fieldname': 'advisor_mon_mor', 'fieldtype': 'Link', 'label': __('Berater/in Mo Vormittag'), 'options': 'Beraterzuweisung'},
        {'fieldname': 'advisor_mon_aft', 'fieldtype': 'Link', 'label': __('Berater/in Mo Nachmittag'), 'options': 'Beraterzuweisung'},
        {'fieldname': 'advisor_tue_mor', 'fieldtype': 'Link', 'label': __('Berater/in Di Vormittag'), 'options': 'Beraterzuweisung'},
        {'fieldname': 'advisor_tue_aft', 'fieldtype': 'Link', 'label': __('Berater/in Di Nachmittag'), 'options': 'Beraterzuweisung'},
        {'fieldname': 'advisor_wed_mor', 'fieldtype': 'Link', 'label': __('Berater/in Mi Vormittag'), 'options': 'Beraterzuweisung'},
        {'fieldname': 'advisor_wed_aft', 'fieldtype': 'Link', 'label': __('Berater/in Mi Nachmittag'), 'options': 'Beraterzuweisung'},
        {'fieldname': 'advisor_thu_mor', 'fieldtype': 'Link', 'label': __('Berater/in Do Vormittag'), 'options': 'Beraterzuweisung'},
        {'fieldname': 'advisor_thu_aft', 'fieldtype': 'Link', 'label': __('Berater/in Do Nachmittag'), 'options': 'Beraterzuweisung'},
        {'fieldname': 'advisor_fri_mor', 'fieldtype': 'Link', 'label': __('Berater/in Fr Vormittag'), 'options': 'Beraterzuweisung'},
        {'fieldname': 'advisor_fri_aft', 'fieldtype': 'Link', 'label': __('Berater/in Fr Nachmittag'), 'options': 'Beraterzuweisung'}
      ],
      'primary_action': function() {
          dialog.hide();
          var options = dialog.get_values();
          fill_date(frm, options)
      },
      'primary_action_label': __('Erstellen')
    });
    dialog.show();
}
