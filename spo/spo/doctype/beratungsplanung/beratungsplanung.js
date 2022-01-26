// Copyright (c) 2021, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Beratungsplanung', {
    button_set_slots: function(frm) {
        if (frm.doc.year) {
            slot_dialog(frm);
        }
    },
    refresh: function(frm) {
        if (!frm.doc.year) {
            cur_frm.set_value("year", (new Date()).getFullYear());
        }
    }
});

function fill_date(frm, options) {
    var year = frm.doc.year;
    var month = frm.doc.month;
    //get nr of days in this month
    var daysInMonth = new Date(year, month, 0).getDate();
    
    //loop, day starts at 1
    for (var day = 1; day <= daysInMonth; day++) {
        //fill in sloteingaben (childtbl)
        //month starts at 0
        var date = new Date(year, month-1, day, 12, 0);                 // use 12 o'clock to prevent UTC shift
        var dayOfWeek = date.getDay();      // 0 = Sunday, 1 = Monday, ... 6 = Saturday
        if ((dayOfWeek > 0) && (dayOfWeek < 6)) {
            // only process for weekdays
            var user = [];
            var time = [];
            var create = false;
            // check if this day is required - Monday
            if (dayOfWeek === 1) {
                if (options.mon_mor === 1) {
                    user.push(options.advisor_mon_mor);
                    time.push("10+11");
                    create = true;
                } 
                if (options.mon_aft === 1) {
                    user.push(options.advisor_mon_aft);
                    time.push("14+15");
                    create = true;
                }
            }
            //Tuesday
            if (dayOfWeek === 2) {
                if (options.tue_mor === 1) {
                    user.push(options.advisor_tue_mor);
                    time.push("10+11");
                    create = true;
                } 
                if (options.tue_aft === 1) {
                    user.push(options.advisor_tue_aft);
                    time.push("14+15");
                    create = true;
                }
            }
            //Wednesday
            if (dayOfWeek === 3) {
                if (options.wed_mor === 1) {
                    user.push(options.advisor_wed_mor);
                    time.push("10+11");
                    create = true;
                }
                if (options.wed_aft === 1) {
                    user.push(options.advisor_wed_aft);
                    time.push("14+15");
                    create = true;
                }
            }
            //Thursday
            if (dayOfWeek === 4) {
                if (options.thu_mor === 1) {
                    user.push(options.advisor_thu_mor);
                    time.push("10+11");
                    create = true;
                }
                if (options.thu_aft === 1) {
                    user.push(options.advisor_thu_aft);
                    time.push("14+15");
                    create = true;
                }
            }
            //Friday
            if (dayOfWeek === 5) {
                if (options.fri_mor === 1) {
                    user.push(options.advisor_fri_mor);
                    time.push("10+11");
                    create = true;
                }
                if (options.fri_aft === 1) {
                    user.push(options.advisor_fri_aft);
                    time.push("14+15");
                    create = true;
                }
            }
            // create
            if (create) {
                for (var k = 0; k < user.length; k++) {
                    var child = cur_frm.add_child('sloteingaben');
                    // set weekday corresponding to options of Sloteingabe Details
                    var weekdays = ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"];
                    
                    frappe.model.set_value(child.doctype, child.name, 'weekday', weekdays[dayOfWeek]);
                    frappe.model.set_value(child.doctype, child.name, 'date', date.toISOString().slice(0, 10));
                    frappe.model.set_value(child.doctype, child.name, 'objective', options.topic);
                    frappe.model.set_value(child.doctype, child.name, 'time', time[k]);
                    frappe.model.set_value(child.doctype, child.name, 'user', user[k]);
                }
            }
        }
    }
    cur_frm.refresh_field('sloteingaben');
}

function slot_dialog(frm) {
    var dialog = new frappe.ui.Dialog({
      'title': __('Welche Slots möchten Sie erstellen?'),
      'fields': [
        {'fieldname': 'topic', 'fieldtype': 'Link', 'label': __('Thema'), 'options': 'Beratungsthema', 'reqd': 1},
        {'fieldname': 'section_main', 'fieldtype': 'Section Break'},
        {'fieldname': 'mon_mor', 'fieldtype': 'Check', 'label': __('Mo Vormittag')},
        {'fieldname': 'mon_aft', 'fieldtype': 'Check', 'label': __('Mo Nachmittag')},
        {'fieldname': 'tue_mor', 'fieldtype': 'Check', 'label': __('Di Vormittag')},
        {'fieldname': 'tue_aft', 'fieldtype': 'Check', 'label': __('Di Nachmittag')},
        {'fieldname': 'wed_mor', 'fieldtype': 'Check', 'label': __('Mi Vormittag')},
        {'fieldname': 'wed_aft', 'fieldtype': 'Check', 'label': __('Mi Nachmittag')},
        {'fieldname': 'thu_mor', 'fieldtype': 'Check', 'label': __('Do Vormittag')},
        {'fieldname': 'thu_aft', 'fieldtype': 'Check', 'label': __('Do Nachmittag')},
        {'fieldname': 'fri_mor', 'fieldtype': 'Check', 'label': __('Fr Vormittag')},
        {'fieldname': 'fri_aft', 'fieldtype': 'Check', 'label': __('Fr Nachmittag')},
        {'fieldname': 'col1', 'fieldtype': 'Column Break'},
        {'fieldname': 'advisor_mon_mor', 'fieldtype': 'Link', 'label': __('Berater/in Mo Vormittag'), 'options': 'Beraterzuweisung'},
        {'fieldname': 'advisor_tue_mor', 'fieldtype': 'Link', 'label': __('Berater/in Di Vormittag'), 'options': 'Beraterzuweisung'},
        {'fieldname': 'advisor_wed_mor', 'fieldtype': 'Link', 'label': __('Berater/in Mi Vormittag'), 'options': 'Beraterzuweisung'},
        {'fieldname': 'advisor_thu_mor', 'fieldtype': 'Link', 'label': __('Berater/in Do Vormittag'), 'options': 'Beraterzuweisung'},
        {'fieldname': 'advisor_fri_mor', 'fieldtype': 'Link', 'label': __('Berater/in Fr Vormittag'), 'options': 'Beraterzuweisung'},
        {'fieldname': 'col2', 'fieldtype': 'Column Break'},
        {'fieldname': 'advisor_mon_aft', 'fieldtype': 'Link', 'label': __('Berater/in Mo Nachmittag'), 'options': 'Beraterzuweisung'},
        {'fieldname': 'advisor_tue_aft', 'fieldtype': 'Link', 'label': __('Berater/in Di Nachmittag'), 'options': 'Beraterzuweisung'},
        {'fieldname': 'advisor_wed_aft', 'fieldtype': 'Link', 'label': __('Berater/in Mi Nachmittag'), 'options': 'Beraterzuweisung'},
        {'fieldname': 'advisor_thu_aft', 'fieldtype': 'Link', 'label': __('Berater/in Do Nachmittag'), 'options': 'Beraterzuweisung'},
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
