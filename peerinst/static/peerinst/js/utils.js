// @flow
"use strict";

export function clear(node: HTMLElement): HTMLElement {
  while (node.hasChildNodes()) {
    // $FlowFixMe
    node.removeChild(node.lastChild);
  }
  return node;
}

export function formatDatetime(datetime: Date): string {
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

export function createSvg(name: string): Element {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
  use.setAttributeNS(
    "http://www.w3.org/1999/xlink",
    "href",
    window.location.protocol +
      "//" +
      window.location.host +
      "/static/peerinst/icons.svg#" +
      name,
  );
  svg.append(use);
  return svg;
}
