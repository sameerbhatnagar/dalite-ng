"use strict";

import { buildReq } from "../_ajax/utils.js";

export function toggleJoinGroup() {
  let box = document.getElementById("student-page-add-group--box");
  if (box.style.display == "none") {
    box.style.display = "flex";
  } else {
    box.style.display = "none";
  }
}

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

export function joinGroup(url, username) {
  let input = document.querySelector("#student-page-add-group--box input");
  let select = document.querySelector("#student-page-add-group--box select");

  let data;
  if (input.value) {
    data = {
      username: username,
      group_link: input.value,
    };
  } else {
    data = {
      username: username,
      group_name: select.value,
    };
  }

  let req = buildReq(data, "post");
  fetch(url, req)
    .then(function(resp) {
      location.reload();
    })
    .catch(function(err) {
      console.log(err);
    });
}

export function leaveGroup(event, url, username, groupName) {
  let groupNode =
    event.currentTarget.parentNode.parentNode.parentNode.parentNode.parentNode;

  let data = {
    username: username,
    group_name: groupName,
  };

  let req = buildReq(data, "post");
  fetch(url, req)
    .then(function(resp) {
      if (resp.ok) {
        groupNode.parentNode.removeChild(groupNode);
      } else {
        console.log(resp);
      }
    })
    .catch(err => console.log(err));
}

export function handleJoinGroupLinkInput(event, url, username) {
  if (event.key === "Enter") {
    joinGroup(url, username);
    event.currentTarget.value = "";
  } else {
    verifyJoinGroupDisabledStatus();
  }
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

export function removeNotification(event, url, notificationPk, link) {
  let notificationNode = event.currentTarget;
  let data = {
    notification_pk: notificationPk,
  };

  let req = buildReq(data, "post");
  fetch(url, req)
    .then(function(resp) {
      if (resp.ok) {
        if (link) {
          window.location = link;
        } else {
          notificationNode.parentNode.removeChild(notificationNode);
        }
      } else {
        console.log(resp);
      }
    })
    .catch(err => console.log(err));
}

function verifyJoinGroupDisabledStatus() {
  let input = document.querySelector("#student-page-add-group--box input");
  let select = document.querySelector("#student-page-add-group--box select");

  if (input.value) {
    select.disabled = true;
  } else {
    select.disabled = false;
  }
}
