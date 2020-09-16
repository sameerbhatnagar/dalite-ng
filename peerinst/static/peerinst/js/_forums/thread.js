export function showReplyForm(id) {
  $(`#${id}`).toggle();
}

export function toggleFollow(el, subscribe, unsubscribe) {
  console.info(el.getAttribute("aria-pressed") === "true");
  if (el.getAttribute("aria-pressed") === "true") {
    console.info("Subscribing to thread");
    const posting = $.post(subscribe);
    posting.done(function (data) {
      //console.info(data);
    });
  } else {
    console.info("Unsubscribing from thread");
    const posting = $.post(unsubscribe);
    posting.done(function (data) {
      //console.info(data);
    });
  }
}

export function initFollows() {
  [].forEach.call(document.querySelectorAll(".mdc-icon-toggle"), (el) => {
    bundle.iconToggle.MDCIconToggle.attachTo(el);
  });
}

export function sizeEmbeddedContent() {
  document.querySelectorAll(".embedded-object").forEach(function (el) {
    const aspectRatio = +el.getAttribute("width") / +el.getAttribute("height");
    const w = Math.min(
      700,
      document.querySelector("section").offsetWidth - 30,
    );
    el.setAttribute("width", w);
    el.setAttribute("height", w / aspectRatio);
  });
}
