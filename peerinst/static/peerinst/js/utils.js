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
  let elem = event.currentTarget;
  elem.classList.add('draggable--dragging');

  event.dataTransfer.effectAllowed = 'move';
  event.dataTransfer.setData('title', elem.getAttribute('data-draggable-name'));
  window.currentDraggedName = elem.getAttribute('data-draggable-name');
}

function handleDragEnd(event) {
  let elem = event.currentTarget;
  elem.classList.remove('draggable--dragging');
  Array.from(elem.parentNode.getElementsByClassName('draggable')).map(x =>
    x.classList.remove('draggable--over'),
  );
}

function handleDragEnter(event) {
  let elem = event.currentTarget;
  let container = elem.parentNode;
  let title = event.dataTransfer.getData('title') || window.currentDraggedName;
  let oldElem = Array.from(container.childNodes).filter(
    x => x.getAttribute('data-draggable-name') == title,
  )[0];
  let oldIdx = Array.from(container.childNodes).indexOf(oldElem);
  let idx = Array.from(container.childNodes).indexOf(elem);
  if (idx > oldIdx) {
    container.insertBefore(oldElem, elem.nextSibling);
  } else if (idx < oldIdx) {
    container.insertBefore(oldElem, elem);
  }
}

function handleDragLeave(event) {
  let elem = event.currentTarget;
  elem.classList.remove('draggable--over');
}

function handleDragOver(event) {
  if (event.preventDefault) {
    event.preventDefault();
  }
  event.dataTransfer.dropEffect = 'move';
  return false;
}

function handleDrop(event) {
  if (event.preventDefault) {
    event.preventDefault();
  }
  if (event.stopPropagation) {
    event.stopPropagation();
  }
  return false;
}

function addEventListeners() {
  Array.from(document.getElementsByClassName('foldable--title')).map(x =>
    x.addEventListener('click', e => toggleFoldable(e)),
  );
  Array.from(document.getElementsByClassName('draggable')).map(x =>
    x.addEventListener('dragstart', e => handleDragStart(e), false),
  );
  Array.from(document.getElementsByClassName('draggable')).map(x =>
    x.addEventListener('dragend', e => handleDragEnd(e), false),
  );
  Array.from(document.getElementsByClassName('draggable')).map(x =>
    x.addEventListener('dragenter', e => handleDragEnter(e), false),
  );
  Array.from(document.getElementsByClassName('draggable')).map(x =>
    x.addEventListener('dragleave', e => handleDragLeave(e), false),
  );
  Array.from(document.getElementsByClassName('draggable')).map(x =>
    x.addEventListener('dragover', e => handleDragOver(e), false),
  );
  Array.from(document.getElementsByClassName('draggable')).map(x =>
    x.addEventListener('drop', e => handleDrop(e), false),
  );
}

export {addEventListeners};
