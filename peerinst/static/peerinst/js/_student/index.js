"use strict";

import { buildReq } from "../_ajax/utils.js";

export function toggleLeaveGroup(event) {
  let element = event.currentTarget;
  let div;
  if (element.tagName == "BUTTON") {
    div = element.parentNode.parentNode;
  } else if (
    element.classList.contains("student-group--remove-confirmation-box")
  ) {
    div = element;
  } else {
    div = element.nextSibling;
  }
  if (div.style.display == "none") {
    div.style.display = "flex";
  } else {
    div.style.display = "none";
  }
}

export function leaveGroup(event, url, username, groupName) {
  let node =
    event.currentTarget.parentNode.parentNode.parentNode.parentNode.parentNode;

  let data = {
    username: username,
    group_name: groupName,
  };

  let req = buildReq(data, "post");
  fetch(url, req).then(function(resp) {
    if (resp.ok) {
      node.parentNode.removeChild(node);
    } else {
      console.log(resp);
    }
  });
}
