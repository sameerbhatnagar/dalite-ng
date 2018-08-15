'use strict';

import {getCsrfToken} from './utils.js';

export function updateAssignmentQuestionList(questionId, assignmentIdentifier) {
  let token = getCsrfToken();
  let data = {
    question_id: questionId,
    assignment_identifier: assignmentIdentifier,
  };
  let req = {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': token,
    },
  };
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
