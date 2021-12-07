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
        frappe.call({
        'method': 'spo.utils.onlinetermin.check_membership',
        'args': {
            'member': customer_nr,
            'lastname': customer_lastname
        },
        'callback': function(response) {
            var details = response.message;
            
            if (details) {
                // got details
                document.getElementById("step4").style.display = "block";
                
                load_calendar(slots);
            } else {
                // invalid call
                document.getElementById("customer_nr").value = null;
                document.getElementById("customer_lastname").value = null;
                document.getElementById("customer_nr").focus();
            }
        }
    });
        // all good, go to next step
        document.getElementById("step1").style.display = "none";
        document.getElementById("step3").style.display = "block";
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
/*
hide selection vor Ort if Erstgespräch
//jQuery('select[name=viewSelector]').change(function(){
    //if option value="f1", hide choices f1
    var fieldsetName = $(this).val();
    $('select[name=choices]').hide().filter('#f1'.show();
});*/
/*
function filter() {
    var keyword = document.getElementById("selector").value;
    var choices = document.getElementById("choices");
    var keyword_txt = keyword.options[keyword.selectedIndex].text;
    if (keyword_txt == 'Ersteinschätzung')
    console.log("ich war in der Ersteinschätzung");
    for (var i = 0; i < choices.length; i++) {
        if (selector.options[i] == 'Termin vor Ort') {
            choices.options[i].style.display = 'none';
        } else {
            choices.options[i].style.display = 'list-item';
        }
    }
*/
/*
function removeAll(choices) {
    while (selectBox.options.length > 0) {
        selectBox.remove(0);
        console.log("removed");
    }
}

*/
