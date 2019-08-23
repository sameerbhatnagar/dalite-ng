"use strict";

const transition = {
  duration: 600,
  direction: "right",
  easing: "easeInOutCubic",
};

export function init(favUrl, refreshUrl) {
  $("#questions .mdc-card").each((i, el) => {
    if (el.getAttribute("initialized") !== "true") {
      el.setAttribute("initialized", "true");

      $(el)
        .find(".mdc-icon-toggle.favourite-btn")
        .each((i, heart) => {
          bundle.iconToggle.MDCIconToggle.attachTo(heart);
          heart.addEventListener("click", () => {
            const posting = $.post(favUrl, {
              pk: heart.getAttribute("data-id"),
            });
            posting.done(data => {
              console.log(data);
            });
          });
        });

      $(el)
        .find(".remove-btn")
        .each((i, x) => {
          x.addEventListener("click", () => {
            const posting = $.get(refreshUrl);
            posting.done(data => {
              $(el).toggle("fade", () => {
                $(el).remove();
                $("#questions").append(data);
                $("#questions .mdc-card")
                  .hide()
                  .toggle("slide", transition);
                init(favUrl, refreshUrl);
              });
            });
            posting.fail(() => {
              x.innerHTML = "error"; // Add snack bar?
              window.setTimeout(() => {
                x.innerHTML = "autorenew";
              }, 5000);
            });
          });
        });
    }
  });
}
