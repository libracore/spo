document.querySelector('nav').remove();
document.querySelector('footer').remove();

var onloadCallback = function() {
    grecaptcha.render('g-recaptcha', {
        'sitekey' : '6LfJyw4cAAAAANc0KKbLSIkqE7TM_1AZyE9tTx4L'
    });
};

function handleSubmit(event, form) {
    event.preventDefault();
    var response = grecaptcha.getResponse();
    console.log(response);
    //recaptcha failed validation
    if (response.length == 0) {
        var recaptcha_error = document.getElementById("recaptcha-error");
        recaptcha_error.innerHTML = 'Bitte bestätigen Sie, dass Sie kein Roboter sind.';
        recaptcha_error.style.display = "block";
        return false;
    } else {
        //recaptcha passed validation
        document.getElementById("recaptcha-error").style.display = "none";
        const jsonFormData = buildJsonFormData(form);
        fetch('https://spo.libracore.ch/api/method/spo.spo.doctype.meldestelle.meldestelle.new_request', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json; charset=UTF-8'
            },
            body: JSON.stringify(jsonFormData)
        })
        .then(r => r.json())
        .then(r => {
            console.log(r);
            if (r.message.success) {
                var modal = document.getElementById("success_modal");
                var span = document.getElementById("success_modal_close");
                span.onclick = function() {
                    modal.style.display = "none";
                    form.reset();
                    location.reload();
                }
                window.onclick = function(event) {
                    if (event.target == modal) {
                        modal.style.display = "none";
                        form.reset();
                        location.reload();
                    }
                }
                modal.style.display = "block";
            } else {
                if (r.message.error == 'reCAPTCHA') {
                    grecaptcha.reset();
                    var recaptcha_error = document.getElementById("recaptcha-error");
                    recaptcha_error.innerHTML = 'Die reCAPTCHA Validierung ist fehlgeschlagen, bitte versuchen Sie es erneut.';
                    recaptcha_error.style.display = "block";
                } else {
                    var modal = document.getElementById("error_modal");
                    var span = document.getElementById("error_modal_close");
                    span.onclick = function() {
                        modal.style.display = "none";
                    }
                    window.onclick = function(event) {
                        if (event.target == modal) {
                            modal.style.display = "none";
                        }
                    }
                    modal.style.display = "block";
                }
            }
        })
    }
}

function buildJsonFormData(form) {
    const jsonFormData = {};
    for(const pair of new FormData(form)) {
        jsonFormData[pair[0]] = pair[1];
    }
    jsonFormData['mandant'] = 'KSA';
    return jsonFormData;
}

var correctCaptcha = function(response) {
    //recaptcha passed validation
    if (response.length != 0) {
        document.getElementById("recaptcha-error").style.display = "none";
    }
};

// Form Event Handler
const form = document.querySelector('form');
form.addEventListener('submit', function(e) {handleSubmit(e, this);});
