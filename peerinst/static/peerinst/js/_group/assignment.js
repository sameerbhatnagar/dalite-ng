"use strict";

import { initStudentProgress } from "./student_progress.js";

function onQuestionListModified() {
  const btn = document.querySelector("#question-list-save");
  btn.disabled = false;
}

function saveQuestionList(url) {
  const questions = Array.from(
    document.querySelectorAll("#question-list .draggable"),
  ).map(x => x.getAttribute("data-draggable-name"));

  const data = { name: "question_list", value: questions };

  const token = document.getElementsByName("csrfmiddlewaretoken")[0].value;

  const req = {
    method: "POST",
    body: JSON.stringify(data),
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": token,
    },
  };

  fetch(url, req).then(function() {
    const btn = document.querySelector("#question-list-save");
    btn.disabled = true;
  });
}

function addAssignmentEventListeners() {
  Array.from(document.querySelectorAll(".draggable")).map(x =>
    x.addEventListener("dragenter", () => onQuestionListModified()),
  );
}

function sendAssignmentEmail(event, url) {
  const icon = event.currentTarget;
  const email = icon.parentNode.parentNode
    .querySelector(".student-list--email")
    .getAttribute("data-email");
  const data = { email: email };
  const token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
  const req = {
    method: "POST",
    body: JSON.stringify(data),
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": token,
    },
  };
  fetch(url, req).then(function(resp) {
    if (resp.ok) {
      icon.style.color = "#00cc66";
      setTimeout(function() {
        icon.style["transition-duration"] = "3s";
      }, 300);
      setTimeout(function() {
        icon.style.color = "#a9a9a9";
        icon.style["transition-duration"] = "none";
      }, 700);
    } else {
      icon.style.color = "#b30000";
      setTimeout(function() {
        icon.style["transition-duration"] = "3s";
      }, 300);
      setTimeout(function() {
        icon.style.color = "#a9a9a9";
        icon.style["transition-duration"] = "none";
      }, 700);
    }
  });
}

function initAssignment(studentProgressUrl) {
  addAssignmentEventListeners();
  initStudentProgress(studentProgressUrl);
}

export { initAssignment, saveQuestionList, sendAssignmentEmail };
