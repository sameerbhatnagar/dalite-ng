'use strict';

import {getCsrfToken} from './utils.js';

export function updateAssignmentQuestionList(url, questionId, assignmentIdentifier) {
  let token = getCsrfToken();
  let data = {
    question_id: questionId,
    assignment_identifier: assignmentIdentifier,
  };
  let req = {
    method: 'POST',
    body: JSON.stringify(data),
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': token,
    },
  };
  fetch(url, req)
    .then(function(resp) {
      if (!resp.ok) {
        console.log(resp);
      } else {
        // Manipulate DOM
        let list = document.getElementById('question-list');
        let card = document.getElementById(questionId);
        if ($.contains(list, card)) {
          $('#'+questionId).remove();
        } else {
          $('#'+questionId).find($( "button" )).html('clear');
          $('#'+questionId).find($('.stats').remove());
          let q = $('#'+questionId).detach();
          q.appendTo($('#question-list'));
          $('#empty-assignment-list').remove();
          $('.search-set').each(function() {
            $(this).find('.filter-count').empty().append($(this).find('.mdc-card:visible').length);
          });
          $('.search-set').each(function() {
            $(this).find('.filter-count-total').empty().append($(this).find('.mdc-card').length);
          });
        }
      }
    })
    .catch(function(err) {
      console.log(err);
    });
}
