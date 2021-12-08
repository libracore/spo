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
    document.getElementById("step2").style.display = "none";
    document.getElementById("step3").style.display = "block";
}

function select_evaluation() {
    document.getElementById("step3").style.display = "none";
    document.getElementById("step4").style.display = "block";
}

function select_consultation() {
    document.getElementById("step3").style.display = "none";
    document.getElementById("step5").style.display = "block";
}

function select_slot() {
    document.getElementById("step4").style.display = "none";
    document.getElementById("step5").style.display = "none";
    
    // call server to get available slots
    frappe.call({
        'method': 'spo.spo.doctype.beratungsslot.beratungsslot.get_slots',
        'callback': function(response) {
            var slots = response.message;
            
            document.getElementById("step6").style.display = "block";
            
            load_calendar(slots);
        }
    });
}

function select_payment() {
    document.getElementById("step6").style.display = "none";
    document.getElementById("step7").style.display = "block";
}

function pay_by_qr() {
    document.getElementById("step7").style.display = "none";
    document.getElementById("step8").style.display = "block";
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
        'events': events
    });
    calendar.render();
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
