"use strict";

export function clear(node) {
  while (node.hasChildNodes()) {
    node.removeChild(node.lastChild);
  }
}

export function formatDatetime(datetime) {
  return (
    datetime.toLocaleString("en-ca", { year: "numeric" }) +
    "-" +
    datetime.toLocaleString("en-ca", { month: "2-digit" }) +
    "-" +
    datetime.toLocaleString("en-ca", { day: "2-digit" }) +
    " " +
    datetime.toLocaleString("en-ca", { hour: "2-digit", hour12: false }) +
    ":" +
    datetime.toLocaleString("en-ca", { minute: "2-digit" })
  );
}
