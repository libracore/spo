document.querySelector('nav').remove();
document.querySelector('footer').remove();

//~ var onloadCallback = function() {
    //~ grecaptcha.render('g-recaptcha-de', {
        //~ 'sitekey' : '6LfJyw4cAAAAANc0KKbLSIkqE7TM_1AZyE9tTx4L'
    //~ });
    //~ grecaptcha.render('g-recaptcha-fr', {
        //~ 'sitekey' : '6LfJyw4cAAAAANc0KKbLSIkqE7TM_1AZyE9tTx4L'
    //~ });
    //~ grecaptcha.render('g-recaptcha-it', {
        //~ 'sitekey' : '6LfJyw4cAAAAANc0KKbLSIkqE7TM_1AZyE9tTx4L'
    //~ });
//~ };

function handleSubmit(event, form) {
    event.preventDefault();
    //~ var response = grecaptcha.getResponse();
    
    var object = buildJsonFormData(form);
    var language = object.language
    //recaptcha failed validation
    //~ if (response.length == 0) {
        //~ var recaptcha_error = document.getElementById("recaptcha-error-"+language);
        //~ if (language == "de") {
            //~ recaptcha_error.innerHTML = "Bitte bestätigen Sie, dass Sie kein Roboter sind.";
        //~ } else if (language == "fr") {
            //~ recaptcha_error.innerHTML = "Veuillez confirmer que vous n'êtes pas un robot.";
        //~ } else if (language == "it") {
            //~ recaptcha_error.innerHTML = "Confermare di non essere un robot.";
        //~ }
        //~ recaptcha_error.style.display = "block";
        //~ return false;
    //~ } else {
        //recaptcha passed validation
        window.scrollTo({ top: 0, behavior: 'smooth' });
        //~ document.getElementById("recaptcha-error").style.display = "none";
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
            //console.log(r);
            if (r.message.success) {
                var modal = document.getElementById("success_modal_"+language);
                var span = document.getElementById("success_modal_close_"+language);
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
            //~ } else {
                //~ if (r.message.error == 'reCAPTCHA') {
                    //~ grecaptcha.reset();
                    //~ var recaptcha_error = document.getElementById("recaptcha-error");
                    //~ if (language == "de") {
                        //~ recaptcha_error.innerHTML = 'Die reCAPTCHA Validierung ist fehlgeschlagen, bitte versuchen Sie es erneut.';
                    //~ } else if (language == "fr") {
                        //~ recaptcha_error.innerHTML = 'La validation reCAPTCHA a échoué, veuillez réessayer.';
                    //~ } else if (language == "it") {
                        //~ recaptcha_error.innerHTML = 'La convalida del reCAPTCHA non è riuscita, riprovare.';
                    //~ }
                    //~ recaptcha_error.style.display = "block";
                } else {
                    var modal = document.getElementById("error_modal_"+language);
                    var span = document.getElementById("error_modal_close_"+language);
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
            //~ }
        })
    //~ }
}

function buildJsonFormData(form) {
    const jsonFormData = {};
    for(const pair of new FormData(form)) {
        jsonFormData[pair[0]] = pair[1];
    }
    jsonFormData['mandant'] = 'KSA';
    return jsonFormData;
}

//~ var correctCaptcha = function(response) {
    //~ //recaptcha passed validation
    //~ if (response.length != 0) {
        //~ document.getElementById("recaptcha-error").style.display = "none";
    //~ }
//~ };

// Form Event Handler
var form_de = document.getElementById('form_de');
form_de.addEventListener('submit', function(e) {handleSubmit(e, this);});
var form_fr = document.getElementById('form_fr');
form_fr.addEventListener('submit', function(e) {handleSubmit(e, this);});
var form_it = document.getElementById('form_it');
form_it.addEventListener('submit', function(e) {handleSubmit(e, this);});
