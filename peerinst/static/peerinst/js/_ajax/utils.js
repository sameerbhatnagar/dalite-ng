"use strict";

export function getCsrfToken() {
  const name = "csrftoken";
  if (document.cookie && document.cookie !== "") {
    return document.cookie
      .split(";")
      .filter(
        c =>
          c
            .replace(/^\s+/, "")
            .replace(/\s+$/, "")
            .substring(0, name.length + 1) ===
          name + "=",
      )
      .map(c => decodeURIComponent(c.substring(name.length + 1)))[0];
  } else {
    return null;
  }
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
