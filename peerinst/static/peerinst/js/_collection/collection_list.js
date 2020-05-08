import { buildReq } from "../ajax.js";

function toggleFollower(pk, teacherToggleFollowerUrl, followersTrans) {
  var posting = $.post(teacherToggleFollowerUrl, {pk: pk});
  posting.done(function(data) {
    const followerValue = parseInt(document.getElementById("follower-count-"+pk).innerHTML.substring(11));
    console.log(data);
    if (data.action == "added") {
      document.getElementById("follower-count-"+pk).innerHTML = (followersTrans + (followerValue+1));
    } else if (data.action == "removed") {
      document.getElementById("follower-count-"+pk).innerHTML = (followersTrans + (followerValue-1));
    }
  });
}

export function init(collectionDetailUrl, toggleFollowerUrl, followersStr){

  $.ajaxSetup({
      beforeSend: function(xhr, settings) {
          if (!bundle.csrfSafeMethod(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", bundle.getCsrfToken());
          }
      }
  });

  [].forEach.call(document.querySelectorAll(".mdc-icon-toggle"), el => {
    bundle.iconToggle.MDCIconToggle.attachTo(el);
  });

  [].forEach.call(document.querySelectorAll(".follower-btn"), el => {
    el.addEventListener("click", () => {
      toggleFollower(el.getAttribute('pk'), toggleFollowerUrl, followersStr);
    });
  });

  [].forEach.call(document.querySelectorAll(".detail-view"), el => {
    el.addEventListener("click", () => {
      window.location.href = collectionDetailUrl.replace("0", el.getAttribute('id'));
    });
  });

}
