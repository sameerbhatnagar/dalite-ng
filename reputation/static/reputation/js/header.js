"use strict";

import { buildReq } from "../../../../peerinst/static/peerinst/js/_ajax/utils.js"; // eslint-disable-line

/*********/
/* model */
/*********/

let model;

function initModel(reputationUrl, reputationType, id) {
  model = {
    reputationUrl: reputationUrl,
    reputationType: reputationType,
    id: id,
    reputation: null,
    reputations: [],
  };
}

/**********/
/* update */
/**********/

async function update() {
  await getReputation();
}

async function getReputation() {
  const postData = {
    reputation_type: model.reputationType,
    id: model.id,
  };
  const req = buildReq(postData, "post");
  const resp = await fetch(model.reputationUrl, req);
  const data = await resp.json();
  model.reputation = data.reputation;
  model.reputations = data.reputations;
}

/********/
/* view */
/********/

function view() {
  iconView();
}

function iconView() {
  if (model.reputation !== null) {
    document.querySelector(
      ".reputation-icon__reputation",
    ).textContent = Math.round(model.reputation * 100);
    document
      .querySelector(".reputation-icon")
      .classList.remove("reputation-icon--hidden");
  }
}

/********/
/* init */
/********/

export async function init(url, reputationType, id) {
  initModel(url, reputationType, id);
  await update();
  view();
}
