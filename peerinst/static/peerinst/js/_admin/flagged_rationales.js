import { buildReq } from "../ajax.js";
import { createElement, createSvg } from "../utils.js";

/*********/
/* model */
/*********/
let model;

function initModel(data) {
  model = {
    data: {
      rationales: [],
      criteria: data.criteria,
    },
    urls: {
      getRationales: data.urls.getRationales,
    },
    config: {
      nPerFetch: 50,
    },
  };
  console.log(model);
}

/**********/
/* update */
/**********/

async function getRationales() {
  let done = false;
  let idx = 0;
  while (!done) {
    const req = buildReq(
      {
        idx: idx,
        n: model.config.nPerFetch,
      },
      "post",
    );
    const resp = await fetch(model.urls.getRationales, req);
    const data = await resp.json();
    model.data.rationales = [...model.data.rationales, data.rationales];
    idx = idx + data.rationales.length;
    done = data.done;
    addRationalesView(data.rationales);
  }
}

/********/
/* view */
/********/

function addRationalesView(rationales) {
  const startingPair =
    (model.data.rationales.length - rationales.length) % 2 == 0;
  rationales.forEach((rationale, i) => {
    const isPair =
      (i % 2 == 0 && startingPair) || (i % 2 == 1 && !startingPair);
    const table = document.querySelector("#flagged-rationales__table");
    table.append(
      createElement("span", rationale.rationale, {
        class: `item rationale ${isPair ? "item--pair" : ""}`,
      }),
    );
    table.append(
      createElement("span", rationale.quality_type, {
        class: `item ${isPair ? "item--pair" : ""}`,
      }),
    );
    model.data.criteria.forEach(criterion => {
      const span = createElement("span", "", {
        class: `item ${isPair ? "item--pair" : ""}`,
      });
      const icon = createSvg("close");
      if (rationale.reasons.some(r => r.full_name == criterion)) {
        icon.classList.add("show");
      }
      span.append(icon);
      table.append(span);
    });
  });
}

/********/
/* init */
/********/

export async function init(data) {
  initModel(data);
  await getRationales();
}
