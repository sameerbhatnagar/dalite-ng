"use strict";

export function clear(node) {
  while (node.hasChildNodes()) {
    node.removeChild(node.lastChild);
  }
}
