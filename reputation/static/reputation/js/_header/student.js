import { buildReq } from "../../../../../peerinst/static/peerinst/js/_ajax/utils.js"; // eslint-disable-line
import { clear } from "../../../../../peerinst/static/peerinst/js/utils.js"; // eslint-disable-line

/*********/
/* model */
/*********/

let model;

function initModel(reputationUrl, reputationType, id) {
  model = {
    reputationListOpen: false,
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

function toggleReputationList() {
  model.reputationListOpen = !model.reputationListOpen;
  reputationListView();
}

/********/
/* view */
/********/

function view() {
  iconView();
  clear(document.querySelector(".reputation-icon__list"));
  reputationListView();
}

function iconView() {
  if (model.reputation !== null) {
    document
      .querySelector(".reputation-icon")
      .classList.remove("reputation-icon--hidden");
  }
}

function reputationListView() {
  if (model.reputationListOpen) {
    document
      .querySelector(".reputation-icon")
      .classList.add("reputation-icon--open");
  } else {
    document
      .querySelector(".reputation-icon")
      .classList.remove("reputation-icon--open");
  }
  const container = document.querySelector(".reputation-icon__list");
  clear(container);
  reputationListHeaderView(container);
  model.reputations.forEach(reputation => {
    reputationView(container, reputation);
  });
}

function reputationListHeaderView(container) {
  const name = document.createElement("div");
  name.classList.add("reputation-icon__list__header");
  name.textContent = "Name";
  container.appendChild(name);

  const weight = document.createElement("div");
  weight.classList.add("reputation-icon__list__header");
  weight.textContent = "Weight";
  container.appendChild(weight);

  const rep = document.createElement("div");
  rep.classList.add("reputation-icon__list__header");
  rep.textContent = "Reputation";
  container.appendChild(rep);
}

function reputationView(container, reputation) {
  const name = document.createElement("div");
  name.classList.add("reputation-icon__list__name");
  name.textContent = `${reputation.full_name} v${reputation.version}`;
  name.title = reputation.description;
  container.appendChild(name);

  const weight = document.createElement("div");
  weight.textContent = reputation.weight;
  container.appendChild(weight);

  const rep = document.createElement("div");
  rep.textContent = Math.round(reputation.reputation * 100);
  container.appendChild(rep);
}

/*************/
/* listeners */
/*************/

function addEventListeners() {
  addReputationListOpenListener();
}

function addReputationListOpenListener() {
  document
    .querySelector(".reputation-icon")
    .addEventListener("click", function(event) {
      event.stopPropagation();
    });
  document
    .querySelector(".reputation-icon__icon")
    .addEventListener("click", function(event) {
      toggleReputationList();
    });
  document.body.addEventListener("click", function(event) {
    if (model.reputationListOpen) {
      toggleReputationList();
    }
  });
}

/********/
/* init */
/********/

export async function init(url, reputationType, id) {
  initModel(url, reputationType, id);
  await update();
  view();
  addEventListeners();
}
