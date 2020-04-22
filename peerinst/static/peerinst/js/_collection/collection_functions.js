export function enumerate(){
  var counter = 1;
  $('.number-box:visible').each(function() {
    var el = $(this).children('.number')[0];
    if (el.innerHTML == "") {
      el.innerHTML = counter;
      counter++;
    }
    return;
  });
}

export function ajaxJQSetup() {
  $.ajaxSetup({
      beforeSend: function(xhr, settings) {
          if (!bundle.csrfSafeMethod(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", bundle.getCsrfToken());
          }
      }
  });
}
