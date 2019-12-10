"use strict";

import { getCsrfToken } from "./utils.js";

export function updateAssignmentQuestionList(
  url,
  questionId,
  assignmentIdentifier,
) {
  const token = getCsrfToken();
  const data = {
    question_id: questionId,
    assignment_identifier: assignmentIdentifier,
  };
  const req = {
    method: "POST",
    body: JSON.stringify(data),
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": token,
    },
  };
  fetch(url, req)
    .then(function(resp) {
      if (!resp.ok) {
        console.log(resp);
      } else {
        // Manipulate DOM
        const list = document.getElementById("question-list");
        const card = document.getElementById(questionId);
        if ($.contains(list, card)) {
          $("#" + questionId).remove();
        } else {
          $("#" + questionId)
            .find($("button"))
            .html("clear");
          $("#" + questionId).find($(".stats").remove());
          const q = $("#" + questionId).detach();
          q.appendTo($("#question-list"));
          $("#empty-assignment-list").remove();
          $(".search-set").each(function() {
            $(this) // eslint-disable-line no-invalid-this
              .find(".filter-count")
              .empty()
              .append($(this).find(".mdc-card:visible").length); // eslint-disable-line no-invalid-this,max-len
          });
          $(".search-set").each(function() {
            $(this) // eslint-disable-line no-invalid-this
              .find(".filter-count-total")
              .empty()
              .append($(this).find(".mdc-card").length); // eslint-disable-line no-invalid-this,max-len
          });
        }
      }
    })
    .catch(function(err) {
      console.log(err);
    });
}