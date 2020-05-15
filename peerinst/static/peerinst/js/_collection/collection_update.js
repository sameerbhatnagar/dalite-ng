import { enumerate, ajaxJQSetup } from "./collection_functions.js";

function toggleAssignment(pk, ppk, toggleUrl) {
  var posting = $.post(toggleUrl, {pk: pk, ppk: ppk});
  posting.done(function(data) {
    console.info(data);
  })
}

export function init(collectionToggleAssignmentUrl){

  ajaxJQSetup();

  [].forEach.call(document.querySelectorAll(".mdc-icon-toggle"), el => {
    bundle.iconToggle.MDCIconToggle.attachTo(el);
  });

  [].forEach.call(document.querySelectorAll(".follower-btn"), el => {
    el.addEventListener("click", () => {
      toggleAssignment(el.getAttribute('pk'), el.getAttribute('ppk'), collectionToggleAssignmentUrl);
    });
  });

  enumerate();
}
