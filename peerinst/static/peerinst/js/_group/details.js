"use strict";
import { buildReq } from "../_ajax/utils.js";

export function removeAssignment(event, url) {
  event.stopPropagation();
  let li = event.currentTarget.parentNode.parentNode;
  let container = li.parentNode;

  let token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
  let req = {
    method: "POST",
    credentials: "include",
    headers: {
      "X-CSRFToken": token,
    },
  };
  url = url + "remove/";

  fetch(url, req).then(function(resp) {
    if (resp.ok) {
      container.removeChild(li.nextSibling);
      container.removeChild(li);

      if (container.childNodes.length == 1) {
        location.reload();
      }
    }
  });
}

export function toggleStudentIdNeeded(event, url) {
  let idNeeded = event.currentTarget.checked;
  let data = {
    name: "student_id_needed",
    value: idNeeded,
  };
  let req = buildReq(data, "post");
  fetch(url, req)
    .then(function(resp) {
      if (!resp.ok) {
        console.log(err);
      }
    })
    .catch(function(err) {
      console.log(err);
    });
}
