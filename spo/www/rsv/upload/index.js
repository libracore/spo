$(document).ready(function() {
    var today = new Date().toISOString().split("T")[0];
    $('#datum').val(today);
});

(function() {
  'use strict';
  window.addEventListener('load', function() {
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.getElementsByClassName('needs-validation');
    // Loop over them and prevent submission
    var validation = Array.prototype.filter.call(forms, function(form) {
      form.addEventListener('submit', function(event) {
        if (form.checkValidity() === false) {
          event.preventDefault();
          event.stopPropagation();
        } else {
            event.preventDefault();
            event.stopPropagation();
            erstelle_anfrage(form);
        }
        form.classList.add('was-validated');
      }, false);
    });
  }, false);
})();

function erstelle_anfrage(form) {
    freeze();
    var form_data = {
        'anlage_key': $(form).attr('anlage_key'),
        'rsv': $(form).attr('rsv')
    };
    for (var i = 0; i < form.length; i++) {
        form_data[form[i].id] = form[i].value;
    }
    
    frappe.call({
        method: "spo.www.rsv.upload.index.erstelle_anfrage",
        args:{
                'form_data': form_data
        },
        freeze: true,
        freeze_message: 'Erstelle Anfrage',
        callback: function(r)
        {
            if (r.message.files > 0) {
                // File Upload
                var file_name = $("#anhang").val().split(/(\\|\/)/g).pop();
                let upload_file = new FormData();
                upload_file.append('file', $("#anhang")[0].files[0], file_name);
                upload_file.append('is_private', 1);
                upload_file.append('doctype', 'Anfrage');
                upload_file.append('docname', r.message.anfrage);
                fetch('/api/method/upload_file', {
                    headers: {
                        'Authorization': 'token ' + r.message.key + ':' + r.message.secret
                    },
                    method: 'POST',
                    body: upload_file
                }).then(function(res){
                    // finish
                    freeze();
                    finish_upload(r.message.anfrage, res.ok);
                });
            } else {
                // finish
                finish_upload(r.message.anfrage, true);
                freeze();
            }
        }
    });
}

function finish_upload(anfrage, good) {
    if (good) {
        frappe.msgprint({
            'title': '<span class="indicator green"></span>Anfrage verarbeitet',
            'message': "Vielen Dank, Ihre Anfrage (" + anfrage + ") wurde erstellt."
        });
    } else {
        frappe.msgprint({
            title: __('<span class="indicator red"></span>Fehlerhafter Datei-Upload'),
            message: "<span class='indicator green spo'></span>Vielen Dank, Ihre Anfrage (" + anfrage + ") wurde erstellt.<br><br><span class='indicator red spo'></span>Leider ist der Datei-Upload fehlgeschlagen.<br>Bitte wenden Sie sich an die SPO."
        });
    }
            
    // reset form
    $('form')[0].reset();
    $('form').removeClass("was-validated");
    var today = new Date().toISOString().split("T")[0];
    $('#datum').val(today);
}

function freeze() {
    $("#formular").toggle("hidden");
    $("#spofreeze").toggle("hidden");
}
