"use strict";

export function getCsrfToken() {
  const name = "csrftoken";
  if (document.cookie && document.cookie !== "") {
    return document.cookie
      .split(";")
      .map(c => c.trim())
      .filter(c => c.substring(0, name.length + 1) === name + "=")
      .map(c => decodeURIComponent(c.substring(name.length + 1)))[0];
  } else {
    return null;
  }
}

export function buildReq(data, method) {
  if (method.toLowerCase() === "get") {
    return {
      method: method.toUpperCase(),
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
    };
  } else if (method.toLowerCase() === "post") {
    const body = data ? JSON.stringify(data) : "";
    return {
      method: method.toUpperCase(),
      body: body,
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
    };
  } else {
    throw Error(`Method ${method} not implemented yet.`);
  }
}
