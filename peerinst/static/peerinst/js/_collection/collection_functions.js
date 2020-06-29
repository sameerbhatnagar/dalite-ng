/* eslint-disable no-invalid-this */
export function enumerate() {
  let counter = 1;
  $(".number-box:visible").each(function () {
    const el = $(this).children(".number")[0];
    if (el.innerHTML == "") {
      el.innerHTML = counter;
      counter++;
    }
    return;
  });
}

export function ajaxJQSetup() {
  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!bundle.csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", bundle.getCsrfToken());
      }
    },
  });
}
