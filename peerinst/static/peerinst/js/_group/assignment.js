'use strict';

function onQuestionListModified() {
  let btn = document.querySelector('#question-list-save');
  btn.disabled = false;
}

function saveQuestionList(url) {
  let questions = Array.from(
    document.querySelectorAll('#question-list .draggable'),
  ).map(x => x.getAttribute('data-draggable-name'));

  let data = {name: 'question_list', value: questions};

  let token = document.getElementsByName('csrfmiddlewaretoken')[0].value;

  let req = {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': token,
    },
  };

  fetch(url, req).then(function() {
    let btn = document.querySelector('#question-list-save');
    btn.disabled = true;
  });
}

function addAssignmentEventListeners() {
  Array.from(document.querySelectorAll('.draggable')).map(x =>
    x.addEventListener('dragenter', () => onQuestionListModified()),
  );
}

export {addAssignmentEventListeners, saveQuestionList};
