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

export function editStudentId(event) {
  let span = event.currentTarget.parentNode.querySelector("span");
  let input = event.currentTarget.parentNode.querySelector("input");
  let copyBtn = event.currentTarget.parentNode.querySelector(
    ".student-group--id__copy",
  );
  let editBtn = event.currentTarget.parentNode.querySelector(
    ".student-group--id__edit",
  );
  let confirmBtn = event.currentTarget.parentNode.querySelector(
    ".student-group--id__confirm",
  );
  let cancelBtn = event.currentTarget.parentNode.querySelector(
    ".student-group--id__cancel",
  );

  input.value = span.textContent;

  span.style.display = "none";
  copyBtn.style.display = "none";
  editBtn.style.display = "none";
  input.style.display = "block";
  confirmBtn.style.display = "flex";
  cancelBtn.style.display = "flex";

  input.focus();
}

export function cancelStudentIdEdition(event) {
  let span = event.currentTarget.parentNode.querySelector("span");
  let input = event.currentTarget.parentNode.querySelector("input");
  let copyBtn = event.currentTarget.parentNode.querySelector(
    ".student-group--id__copy",
  );
  let editBtn = event.currentTarget.parentNode.querySelector(
    ".student-group--id__edit",
  );
  let confirmBtn = event.currentTarget.parentNode.querySelector(
    ".student-group--id__confirm",
  );
  let cancelBtn = event.currentTarget.parentNode.querySelector(
    ".student-group--id__cancel",
  );

  span.style.display = "flex";
  copyBtn.style.display = "flex";
  editBtn.style.display = "flex";
  input.style.display = "none";
  confirmBtn.style.display = "none";
  cancelBtn.style.display = "none";
}

export function saveStudentId(event, url, groupName) {
  let span = event.currentTarget.parentNode.querySelector("span");
  let input = event.currentTarget.parentNode.querySelector("input");
  let copyBtn = event.currentTarget.parentNode.querySelector(
    ".student-group--id__copy",
  );
  let editBtn = event.currentTarget.parentNode.querySelector(
    ".student-group--id__edit",
  );
  let confirmBtn = event.currentTarget.parentNode.querySelector(
    ".student-group--id__confirm",
  );
  let cancelBtn = event.currentTarget.parentNode.querySelector(
    ".student-group--id__cancel",
  );

  let data = {
    student_id: input.value,
    group_name: groupName,
  };

  let req = buildReq(data, "post");
  fetch(url, req)
    .then(function(resp) {
      location.reload();
    })
    .catch(function(err) {
      console.log(err);
    });
}

export function handleStudentIdKeyDown(event, url, groupName) {
  if (event.key === "Enter") {
    saveStudentId(event, url, groupName);
  } else if (event.key === "Escape") {
    cancelStudentIdEdition(event);
  }
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
