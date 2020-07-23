"use strict";

function getCsrfToken() {
  return document.querySelectorAll("input[name=csrfmiddlewaretoken]")[0].value;
}

async function handleResponse(response) {
  if (response.status == 200 || response.status == 201) {
    return await response.json();
  }

  if (response.status == 401) {
    const data = await response.json();
    const base = new URL(window.location.protocol + window.location.host);
    const url = new URL(data["login_url"], base);
    url.search = `?next=${window.location.pathname}`;
    console.debug(url);
    window.location.href = url;
  }

  if ([400, 403, 404, 405].includes(response.status)) {
    console.info(response);
    throw new Error(response);
  }
}

export async function submitData(url, data, method) {
  const response = await fetch(url, {
    method,
    mode: "same-origin",
    cache: "no-cache",
    credentials: "same-origin",
    redirect: "follow",
    referrer: "client",
    headers: new Headers({
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    }),
    body: JSON.stringify(data),
  });
  return await handleResponse(response);
}

export async function get(url) {
  const response = await fetch(url, {
    method: "GET",
    mode: "same-origin",
    cache: "no-cache",
    credentials: "same-origin",
    redirect: "follow",
    referrer: "client",
  });

  return await handleResponse(response);
}
