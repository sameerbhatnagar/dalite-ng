"use strict";

export function createInput(type) {
  const input = document.createElement("input");
  if (type === "PositiveIntegerField") {
    input.type = "number";
    input.min = 0;
  } else if (type === "ProbabilityField") {
    input.type = "number";
    input.min = 0;
    input.max = 1;
    input.step = 0.01;
  }
  return input;
}
