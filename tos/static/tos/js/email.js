'use strict';

function toggleButton(event) {
  let container = event.currentTarget;
  if (!container.classList.contains('btn-toggle--disabled')) {
    let buttons = container.getElementsByTagName('div');
    let checkbox = container.getElementsByTagName('input')[0];
    if (checkbox.checked) {
      checkbox.checked = false;
      buttons[0].classList.remove('btn-toggle--selected');
      buttons[1].classList.add('btn-toggle--selected');
    } else {
      checkbox.checked = true;
      buttons[0].classList.add('btn-toggle--selected');
      buttons[1].classList.remove('btn-toggle--selected');
    }
  }
}

function toggleButtonAll(event) {
  let container = event.currentTarget;
  let checkbox = container.getElementsByTagName('input')[0];
  if (checkbox.checked) {
    let toggleButtons = document.getElementsByClassName('btn-toggle');
    for (let i = 0; i < toggleButtons.length; i++) {
      toggleButtons[i].classList.remove('btn-toggle--disabled');
    }
  } else {
    let toggleButtons = document.getElementsByClassName('btn-toggle');
    for (let i = 0; i < toggleButtons.length; i++) {
      if (toggleButtons[i] != container) {
        toggleButtons[i].classList.add('btn-toggle--disabled');
      }
    }
  }
}

Array.from(document.getElementsByClassName('btn-toggle')).map(x =>
  x.addEventListener('click', e => toggleButton(e)),
);

let toggleAll = document.getElementById('btn-toggle-all');
if (toggleAll) {
  toggleAll.addEventListener('click', e => toggleButtonAll(e));
}
