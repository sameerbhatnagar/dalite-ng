'use strict';

import {
  addStudentProgressView,
  toggleStudentProgressView,
} from './student_progress.js';

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
    credentials: 'include',
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

function sendAssignmentEmail(event, url) {
  let icon = event.currentTarget;
  let email = icon.parentNode.parentNode
    .querySelector('.student-list--email')
    .getAttribute('data-email');
  let data = {email: email};
  let token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
  let req = {
    method: 'POST',
    body: JSON.stringify(data),
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': token,
    },
  };
  fetch(url, req).then(function(resp) {
    if (resp.ok) {
      icon.style.color = '#00cc66';
      setTimeout(function() {
        icon.style['transition-duration'] = '3s';
      }, 300);
      setTimeout(function() {
        icon.style.color = '#a9a9a9';
        icon.style['transition-duration'] = 'none';
      }, 700);
    } else {
      icon.style.color = '#b30000';
      setTimeout(function() {
        icon.style['transition-duration'] = '3s';
      }, 300);
      setTimeout(function() {
        icon.style.color = '#a9a9a9';
        icon.style['transition-duration'] = 'none';
      }, 700);
    }
  });
}

function setUpAssignmentPage() {
  addAssignmentEventListeners();
  addStudentProgressView();
}

export {
  setUpAssignmentPage,
  saveQuestionList,
  sendAssignmentEmail,
  toggleStudentProgressView,
};
