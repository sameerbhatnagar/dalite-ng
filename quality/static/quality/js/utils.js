"use strict";

export function createInput(type) {
  const input = document.createElement("input");
  if (type === "PositiveIntegerField") {
    input.type = "number";
    input.min = 0;
  }
  return input;
}
