"use strict";

const transition = {
  duration: 600,
  direction: "right",
  easing: "easeInOutCubic",
};

export function init(url) {
  // Rating system
  $("#rationales .mdc-card").each((i, el) => {
    const id = el.getAttribute("data-id");
    const submitBtn = document.getElementById("submit-score-btn");
    let score;

    $(".star").each((i, star) => {
      star.addEventListener("click", () => {
        submitBtn.removeAttribute("disabled");
        score = star.getAttribute("data-rank");
        $(".star").each((i, _star) => {
          if (_star.getAttribute("data-rank") <= score) {
            _star.innerHTML = "star";
          } else {
            _star.innerHTML = "star_border";
          }
        });
      });
    });

    // Submit score
    submitBtn.addEventListener("click", () => {
      const posting = $.post(url, { id: id, score: score });
      posting.done(data => {
        processResponse(data);
      });
    });

    // Flag inappropriate
    const flagBtn = document.getElementById("submit-flag-btn");
    flagBtn.addEventListener("click", () => {
      const posting = $.post(url, { id: id, score: 0 });
      posting.done(data => {
        processResponse(data);
      });
    });

    function processResponse(data) {
      $(el).toggle("fade", () => {
        $(el).remove();
        $("#rationales").append(data);
        $("#rationales .mdc-card")
          .hide()
          .toggle("slide", transition);
        init(url);
      });
    }
  });
}
