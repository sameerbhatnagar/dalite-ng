'use strict';

function toggleFoldable(event) {
  let foldable = event.currentTarget.parentNode;
  if (foldable.classList.contains('foldable__unfolded')) {
    foldable.classList.remove('foldable__unfolded');
  } else {
    foldable.classList.add('foldable__unfolded');
  }
}

export {toggleFoldable};
