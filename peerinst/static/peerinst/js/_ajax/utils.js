"use strict";

export function getCsrfToken() {
  const name = "csrftoken";
  if (document.cookie && document.cookie !== "") {
    return document.cookie
      .split(";")
      .map(c => c.replace(/^\s+/, "").replace(/\s+$/, ""))
      .filter(c => c.substring(0, name.length + 1) === name + "=")
      .map(c => decodeURIComponent(c.substring(name.length + 1)))[0];
  } else {
    return null;
  }
}

export function buildReq(data, method) {
  console.log(getCsrfToken());
  return {
    method: method.toUpperCase(),
    body: JSON.stringify(data),
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    },
  };
}
