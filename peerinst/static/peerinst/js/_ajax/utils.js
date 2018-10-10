"use strict";

export function getCsrfToken() {
  return document.getElementsByName("csrfmiddlewaretoken")[0].value;
}

export function buildReq(data, method) {
  return {
    method: method.toUpperCase(),
    body: JSON.stringify(data),
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    },
  };
}
