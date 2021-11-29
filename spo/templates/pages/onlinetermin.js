/*script.js, ab Zeile 71 calendar, ab 135 main ersetzt durch fullcalendar(für kalender,riesig)*/
$(function() {
    $('#navbar').affix({
        offset: {
            top: 200
        }
    });

    $("pre.html").snippet("html", {style:'matlab'});
    $("pre.css").snippet("css", {style:'matlab'});
    $("pre.javascript").snippet("javascript", {style:'matlab'});

    $('#myWizard').easyWizard({
        buttonsClass: 'btn',
        submitButtonClass: 'btn btn-info'
    });

    $('#myWizard2').easyWizard({
        buttonsClass: 'btn',
        submitButtonClass: 'btn btn-info',
        before: function(wizardObj, currentStepObj, nextStepObj) {
            /*var r = true;
            wizardObj.find('input, textarea').each(function() {
                if(!this.checkValidity()) {
                    r = false;
                }
            });
            
            return r;*/
        },
        after: function(wizardObj, prevStepObj, currentStepObj) {
            /*alert('Hello, I\'am the after callback');*/
        },
        beforeSubmit: function(wizardObj) {
            /*alert('Hello, I\'am the beforeSubmit callback');*/
            /*hier kalender von hide zu show, und header hide?*/
        }
    });

/*Um eigene Buttons zu verwenden, Problem: haben 1 Form, nicht pro Slide, mywizard3 ist form id*/
    $('#myWizard3').easyWizard({
        showSteps: false,
        showButtons: false,
        submitButton: false
    });
    $('#myWizard3Pager .previous a').bind('click', function(e) {
        e.preventDefault();
        $('#myWizard3').easyWizard('prevStep');
    });
    $('#myWizard3Pager .page a').bind('click', function(e) {
        e.preventDefault();
        $('#myWizard3').easyWizard('goToStep', $(this).attr('rel'));
    });
    $('#myWizard3Pager .next a').bind('click', function(e) {
        e.preventDefault();
        $('#myWizard3').easyWizard('nextStep');
    });
});

/*neu hinzugefügt*/
function hide_content() {
    var x = document.getElementById("calendar");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}


/*calender.js */
document.addEventListener('DOMContentLoaded', function() {
  var calendarEl = document.getElementById('calendar');

  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    initialDate: '2021-10-03',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay'
    },
    events: [
    {
        title: '08:00',
        start: '2021-10-01 '
      },
      {
        title: '09:00',
        start: '2021-10-01'
      },
      {
        title: '16:00',
        start: '2021-10-01'
      },
            {
        title: '10:00',
        start: '2021-10-05'
      },
            {
        title: '13:00',
        start: '2021-10-05'
      },
            {
        title: '15:00',
        start: '2021-10-05'
      },
      {
        title: '08:00',
        start: '2021-10-07'
      },
            {
        title: '09:00',
        start: '2021-10-07'
      },
      {
        title: '11:00',
        start: '2021-10-12'
      },
      {
        title: '13:00',
        start: '2021-10-07'
      },
      {
        title: '15:00',
        start: '2021-10-12',

      }
    ]
  });

  calendar.render();
});

/*main.js des kalenders ersetzt durch /assets/frappe/js/lib/fullcalendar*/
/*!
FullCalendar v5.10.1
Docs & License: https://fullcalendar.io/
(c) 2021 Adam Shaw
*/
