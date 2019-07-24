"use strict";
import { buildReq } from "../ajax.js";

export function removeAssignment(event, url) {
  event.stopPropagation();
  const li = event.currentTarget.parentNode.parentNode;
  const container = li.parentNode;

  const token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
  const req = {
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

      if (container.children.length == 1) {
        location.reload();
      }
    }
  });
}

export function toggleStudentIdNeeded(event, url) {
  const idNeeded = event.currentTarget.checked;
  const data = {
    name: "student_id_needed",
    value: idNeeded,
  };
  const req = buildReq(data, "post");
  fetch(url, req)
    .then(function(resp) {
      if (!resp.ok) {
        console.log(resp);
      }
    })
    .catch(function(err) {
      console.log(err);
    });
}
