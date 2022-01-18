// navigation
function start() {
    document.getElementById("step0").style.display = "block";
    document.getElementById("step1").style.display = "none";
    document.getElementById("step2").style.display = "none";
    document.getElementById("step3").style.display = "none";
    document.getElementById("step6").style.display = "none";
    document.getElementById("step7").style.display = "none";
    document.getElementById("step10").style.display = "none";
}

function is_member() {
    document.getElementById("step0").style.display = "none";
    document.getElementById("step1").style.display = "block";
}

function is_nonmember() {
    document.getElementById("step0").style.display = "none";
    document.getElementById("step2").style.display = "block";
}

function start_over() {
    document.getElementById("step0").style.display = "block";
    document.getElementById("step1").style.display = "none";
    document.getElementById("step2").style.display = "none";
}


function select_option_from_member() {
    var customer_nr = document.getElementById("customer_nr").value;
    var customer_lastname = document.getElementById("customer_lastname").value;
    if (!customer_nr) {
        document.getElementById("customer_nr").style.border = "1px solid red;"
        document.getElementById("customer_nr").focus();
    } else if (!customer_lastname) {
        document.getElementById("customer_lastname").style.border = "1px solid red;"
        document.getElementById("customer_lastname").focus();
    } else {
        // verify membership
        document.getElementById("member_wait").style.display = "block"; // waiting gif
        document.getElementById("member_buttons").style.display = "none"; // buttons off
        frappe.call({
            'method': 'spo.utils.onlinetermin.check_membership',
            'args': {
                'member': customer_nr,
                'lastname': customer_lastname
            },
            'callback': function(response) {
                // disable waiting animation
                document.getElementById("member_wait").style.display = "none";
                document.getElementById("member_buttons").style.display = "block"; // buttons back on
                var details = response.message;
                if (details) {
                    // got details, store them in the form
                    document.getElementById("inputFirstname").value = details.first_name;
                    document.getElementById("inputSurname").value = details.last_name;
                    document.getElementById("inputStreet").value = details.address_line1;
                    document.getElementById("inputCity").value = details.city;
                    document.getElementById("inputZIP").value = details.pincode;
                    document.getElementById("inputEmail").value = details.email_id;
                    document.getElementById("inputPhone").value = details.phone;
                    document.getElementById("used_slots").value = details.used_slots;
                    
                    // open step 3: select options
                    document.getElementById("step1").style.display = "none";
                    document.getElementById("step3").style.display = "block";
    
                } else {
                    // invalid call
                    document.getElementById("member_failed").style.display = "block";
                    document.getElementById("customer_nr").value = null;
                    document.getElementById("customer_lastname").value = null;
                    document.getElementById("customer_nr").focus();
                }
            }
        });
    }
}

function back_to_options() {
    document.getElementById("step3").style.display = "block";
    document.getElementById("step6").style.display = "none";
}

function select_option_from_nonmember() {
    var firstname = document.getElementById("inputFirstname").value;
    var lastname = document.getElementById("inputSurname").value;
    var email = document.getElementById("inputEmail").value;
    var phone = document.getElementById("inputPhone").value;
    var street = document.getElementById("inputStreet").value;
    var zip = document.getElementById("inputZIP").value;
    var city = document.getElementById("inputCity").value;
    if (!firstname) {
        document.getElementById("inputFirstname").style.border = "1px solid red;"
        document.getElementById("inputFirstname").focus();
    } else if (!lastname) {
        document.getElementById("inputSurname").style.border = "1px solid red;"
        document.getElementById("inputSurname").focus();
    } else if (!email) {
        document.getElementById("inputEmail").style.border = "1px solid red;"
        document.getElementById("inputEmail").focus();
    } else if (!phone) {
        document.getElementById("inputPhone").style.border = "1px solid red;"
        document.getElementById("inputPhone").focus();
    } else if (!street) {
        document.getElementById("inputStreet").style.border = "1px solid red;"
        document.getElementById("inputStreet").focus();
    } else if (!zip) {
        document.getElementById("inputZIP").style.border = "1px solid red;"
        document.getElementById("inputZIP").focus();
    } else if (!city) {
        document.getElementById("inputCity").style.border = "1px solid red;"
        document.getElementById("inputCity").focus();
    } else {
    document.getElementById("step2").style.display = "none";
    document.getElementById("step3").style.display = "block";
    }
}

function select_slot() {
    document.getElementById("step3").style.display = "none";
    
    // call server to get available slots
    frappe.call({
        'method': 'spo.spo.doctype.beratungsslot.beratungsslot.get_slots',
        'args': {
            'topic': document.getElementById("topic").value
        },
        'callback': function(response) {
            var slots = response.message;
            
            document.getElementById("step6").style.display = "block";
            document.getElementById("calendar").style.display = "block";
            document.getElementById("calendar_wait").style.display = "none";
            
            load_calendar(slots);
        }
    });
}

// this function is called when a calender slot is selected
function reserve_slot(id, title, start) {
    // hide calendar to prevent double-hits
    document.getElementById("calendar").style.display = "none";
    document.getElementById("calendar_wait").style.display = "block";
    
    // reserve slot
    frappe.call({
        'method': 'spo.spo.doctype.beratungsslot.beratungsslot.reserve_slot',
        'args': {
            'slot': id,
            'member': document.getElementById("customer_nr").value, 
            'first_name': document.getElementById("inputFirstname").value, 
            'last_name': document.getElementById("inputSurname").value, 
            'address': document.getElementById("inputStreet").value, 
            'city': document.getElementById("inputCity").value, 
            'pincode': document.getElementById("inputZIP").value, 
            'email': document.getElementById("inputEmail").value, 
            'phone': document.getElementById("inputPhone").value,
            'used_slots': document.getElementById("used_slots").value,
            'consultation_type': document.getElementById("consultation_mode").value,
            'text': document.getElementById("text").value,
            'geburtsdatum': document.getElementById("inputBirthdate").value,
            'salutation_title': document.getElementById("salutation_title").value
        },
        'callback': function(response) {
            var success = response.message;
            
            if (success) {
                document.getElementById("slot_id").value = id;
                document.getElementById("slot_title").value = title;
                document.getElementById("slot_start").value = start.toLocaleString("de-ch", {weekday: "long", year: "numeric", month: "numeric", day: "numeric", hour: "numeric", minute: "numeric"});   
                document.getElementById("slot_title_final").value = title;
                document.getElementById("slot_start_final").value = start.toLocaleString("de-ch", {weekday: "long", year: "numeric", month: "numeric", day: "numeric", hour: "numeric", minute: "numeric"});   
                
                select_payment();
            } else {
                // remain on calendar, could not lock this slot
                console.log("slot reservation failed: " + id);
            }
        }
    });
    
    
}

function select_payment() {
    // check if a payment is required
    if (parseInt(document.getElementById("used_slots").value, 10) === 0) {
        // member with no used slots --> consider paid
        done();
    } else {
        // requires payment
        create_invoice();
    }
}

function create_invoice() {
    frappe.call({
        'method': 'spo.utils.onlinetermin.submit_request',
        'args': {
            'slot': document.getElementById("slot_id").value, 
            'member': document.getElementById("customer_nr").value, 
            'first_name': document.getElementById("inputFirstname").value, 
            'last_name': document.getElementById("inputSurname").value, 
            'address': document.getElementById("inputStreet").value, 
            'city': document.getElementById("inputCity").value, 
            'pincode': document.getElementById("inputZIP").value, 
            'email': document.getElementById("inputEmail").value, 
            'phone': document.getElementById("inputPhone").value,
            'geburtsdatum': document.getElementById("inputBirthdate").value,
            'salutation_title': document.getElementById("salutation_title").value,
        },
        'callback': function(response) {
            // invoice created
            var payment = response.message;
            
            // insert payrexx iframe here
            console.log(payment['link']);
            document.getElementById("payrexx").innerHTML = 
                "<iframe src=\"" + payment['link'] + "\" title=\"Payrexx payment\""
                + " frameborder=\"0\" style=\"width: 100%; height: 750px; \"></iframe>";
                
            // open payrexx page
            document.getElementById("step6").style.display = "none";    // disable calendar
            document.getElementById("step7").style.display = "block";
        }
    });
}

function done() {
    document.getElementById("step0").style.display = "none";
    document.getElementById("step6").style.display = "none";
    document.getElementById("step7").style.display = "none";
    document.getElementById("step10").style.display = "block";
}

function load_calendar(events) {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
      'initialView': 'dayGridMonth',
      'headerToolbar': {
          'left': 'prev,next today',
          'center': 'title',
          'right': 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        'events': events,
        'locale': 'de',
        'eventClick': function(info) {
            reserve_slot(info.event.id, info.event.extendedProps.description, info.event.start);
        },
        'eventColor': '#ffffff'
    });
    calendar.render();
}

//change triggers
document.addEventListener("DOMContentLoaded", function(event) {
    // add change triggers here
    
    // process command line arguments
    get_arguments();
});

function get_arguments() {
    var arguments = window.location.toString().split("?");
    if (!arguments[arguments.length - 1].startsWith("http")) {
        var args_raw = arguments[arguments.length - 1].split("&");
        var args = {};
        args_raw.forEach(function (arg) {
            var kv = arg.split("=");
            if (kv.length > 1) {
                args[kv[0]] = kv[1];
            }
        });
        if (args['success']) {
            // this is a success postback
            done();
            // fetch payment status
            fetch_payment_status(args['success']);
        }
    } 
}

function fetch_payment_status(booking) {
    frappe.call({
        'method': 'spo.utils.onlinetermin.fetch_payment_status',
        'args': {
            'booking': booking
        },
        'callback': function(response) {
            // do nothing
        }
    });
}
