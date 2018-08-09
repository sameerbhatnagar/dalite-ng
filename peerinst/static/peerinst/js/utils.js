'use strict';

function toggleFoldable(event) {
  let foldable = event.currentTarget.parentNode;
  if (foldable.classList.contains('foldable__unfolded')) {
    foldable.classList.remove('foldable__unfolded');
    foldable.childNodes[1].style.overflow = 'hidden';
  } else {
    foldable.classList.add('foldable__unfolded');
    setTimeout(function() {
      foldable.childNodes[1].style.overflow = 'auto';
    }, 300);
  }
}

function handleDragStart(event) {
  event.dataTransfer.effectAllowed = 'move';
  event.dataTransfer.setData('text/html', 'data');

  let elem = event.currentTarget;
  elem.style.opacity = '0.5';
}

function addEventListeners() {
  Array.from(document.getElementsByClassName('foldable--title')).map(x =>
    x.addEventListener('click', e => toggleFoldable(e)),
  );
  Array.from(document.getElementsByClassName('draggable')).map(x =>
    x.addEventListener('dragstart', e => handleDragStart(e), false),
  );
}

export {addEventListeners};
