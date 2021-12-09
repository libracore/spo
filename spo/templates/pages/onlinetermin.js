// navigation
function start() {
    document.getElementById("step0").style.display = "block";
    document.getElementById("step1").style.display = "none";
    document.getElementById("step2").style.display = "none";
    document.getElementById("step3").style.display = "none";
    document.getElementById("step4").style.display = "none";
    document.getElementById("step5").style.display = "none";
    document.getElementById("step6").style.display = "none";
    document.getElementById("step7").style.display = "none";
    document.getElementById("step8").style.display = "none";
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

function select_option_from_nonmember() {
    var firstname = document.getElementById("firstname").value;
    var lastname = document.getElementById("surname").value;
    var email = document.getElementById("email").value;
    var phone = document.getElementById("phone").value;
    var street = document.getElementById("street").value;
    var zip = document.getElementById("zip").value;
    var city = document.getElementById("city").value;
    if (!firstname) {
        document.getElementById("firstname").style.border = "1px solid red;"
        document.getElementById("firstname").focus();
    } else if (!lastname) {
        document.getElementById("surname").style.border = "1px solid red;"
        document.getElementById("surname").focus();
    } else if (!email) {
        document.getElementById("email").style.border = "1px solid red;"
        document.getElementById("email").focus();
    } else if (!phone) {
        document.getElementById("phone").style.border = "1px solid red;"
        document.getElementById("phone").focus();
    } else if (!street) {
        document.getElementById("street").style.border = "1px solid red;"
        document.getElementById("street").focus();
    } else if (!zip) {
        document.getElementById("zip").style.border = "1px solid red;"
        document.getElementById("zip").focus();
    } else if (!city) {
        document.getElementById("city").style.border = "1px solid red;"
        document.getElementById("city").focus();
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
            
            load_calendar(slots);
        }
    });
}

// this function is called when a calender slot is selected
function reserve_slot(id, title, start) {
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
            'phone': document.getElementById("inputPhone").value
        },
        'callback': function(response) {
            var success = response.message;
            
            if (success) {
                document.getElementById("slot_id").value = id;
                document.getElementById("slot_title").value = title;
                document.getElementById("slot_start").value = start;
                
                select_payment();
            } else {
                // remain on calendar, could not lock this slot
                console.log("slot reservation failed: " + id);
            }
        }
    });
    
    
}

function select_payment() {
    document.getElementById("step6").style.display = "none";
    document.getElementById("step7").style.display = "block";
}

function pay_by_qr() {
    // load QR code
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
            'phone': document.getElementById("inputPhone").value
        },
        'callback': function(response) {
            // invoice created
            var details = response.message;
            
            var qr_source = "https://data.libracore.ch/phpqrcode/api/iso20022.php?"
                + "iban=CH7400700110304209806&"
                + "receiver_name=SPO Schweizerische Patientenorganisation&" 
                + "receiver_street=Häringstrasse&"
                + "receiver_number=20&"
                + "receiver_pincode=8001&"
                + "receiver_town=Zürich&"
                + "receiver_country=CH&"
                + "amount=" + details.rate + "&"
                + "currency=CHF&"
                + "payer_name=" + document.getElementById("inputFirstname").value + " " + document.getElementById("inputSurname").value + "&" 
                + "payer_street=" + document.getElementById("inputStreet").value + "&"
                + "payer_number=&"
                + "payer_pincode=" + document.getElementById("inputZIP").value + "&" 
                + "payer_town=" + document.getElementById("inputCity").value +"&"
                + "payer_country=CH&"
                + "reference_type=NON&message=" + details.invoice;

            document.getElementById("qr_code").src = qr_source;

            document.getElementById("step7").style.display = "none";
            document.getElementById("step8").style.display = "block";
        }
    });
        
    
}

function pay_stripe() {
    document.getElementById("step7").style.display = "none";
    document.getElementById("step9").style.display = "block";
}

function done() {
    document.getElementById("step8").style.display = "none";
    document.getElementById("step9").style.display = "none";
    document.getElementById("step10").style.display = "block";
}

function load_calendar(events) {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
      'initialView': 'dayGridMonth',
      'headerToolbar': {
          'left': 'prev,next today',
          'center': 'title',
          'right': 'dayGridMonth,timeGridWeek,timeGrudDay'
        },
        'events': events,
        'eventClick': function(info) {
            reserve_slot(info.event.id, info.event.title, info.event.start);
        }
    });
    calendar.render();
}

// this function will create the sales invoice (and if required the customer)
function create_invoice() {
    
}

//change triggers
document.addEventListener("DOMContentLoaded", function(event) {
    // when document is loaded, add change triggers
    document.getElementById("consultation_type").onchange = function() {
        if (document.getElementById("consultation_type").value === "Ersteinschätzung") {
            document.getElementById("consultation_mode_onsite").disabled = true;
            if (document.getElementById("consultation_mode_onsite").selected) {
                document.getElementById("consultation_mode_phone").selected = true;
            }
        } else {
            document.getElementById("consultation_mode_onsite").disabled = false;
        }
    }
});
