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
  let groupNode =
    event.currentTarget.parentNode.parentNode.parentNode.parentNode.parentNode;

  let data = {
    username: username,
    group_name: groupName,
  };

  let req = buildReq(data, "post");
  fetch(url, req).then(function(resp) {
    if (resp.ok) {
      groupNode.parentNode.removeChild(groupNode);
    } else {
      console.log(resp);
    }
  });
}

export function toggleGroupNotifications(event, url, username, groupName) {
  let icon = event.currentTarget;

  let data = {
    username: username,
    group_name: groupName,
  };

  let req = buildReq(data, "post");
  fetch(url, req)
    .then(resp => resp.json())
    .then(function(data) {
      if (data.notifications) {
        icon.textContent = "notifications";
        icon.classList.remove("student-group--notifications__disabled");
      } else {
        icon.textContent = "notifications_off";
        icon.classList.add("student-group--notifications__disabled");
      }
    })
    .catch(function(err) {
      console.log(err);
    });
}
