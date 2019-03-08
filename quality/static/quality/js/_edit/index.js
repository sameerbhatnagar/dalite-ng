"use strict";

import { buildReq } from "../../../../../peerinst/static/peerinst/js/_ajax/utils.js"; // eslint-disable-line

/*********/
/* model */
/*********/

let model;

function initModel(data) {
  model = {
    quality: {
      pk: data.quality.pk,
      qualityType: data.quality.quality_type,
    },
    next: data.next,
    available: data.available.map(c => ({
      name: c.name,
      fullName: c.full_name,
      description: c.description,
    })),
    criterions: data.criterions,
    urls: {
      addCriterion: data.urls.add_criterion,
    },
  };
}

/**********/
/* update */
/**********/

function addCriterion(criterion) {
  const data = {
    quality: model.quality.pk,
    criterion: criterion,
  };

  const req = buildReq(data, "post");
  fetch(model.urls.addCriterion, req)
    .then(resp => resp.json())
    .then(json => console.log(json))
    .catch(err => console.log(err));
}

/********/
/* view */
/********/

function view() {
  returnLinkView();
  criterionsView();
  newCriterionsView();
}

function returnLinkView() {
  const link = document.querySelector("#back-link");
  if (model.next) {
    link.href = model.next;
    link.textContent = `Back to ${model.quality.qualityType}`;
  } else {
    link.parentNode.removeChild(link);
  }
}

function criterionsView() {
  const div = document.querySelector("#criterions");
  model.criterions.forEach(criterion => {
    div.appendChild(criterionView(criterion));
  });
}

function criterionView(criterion) {
  const div = document.createElement("div");
  div.classList.add("criterion");

  const name = document.createElement("div");
  name.classList.add("criterion--name");
  name.textContent = criterion.name;
  div.appendChild(name);

  const options = document.createElement("div");
  options.classList.add("criterion--options");
  div.appendChild(options);

  return div;
}

function newCriterionsView() {
  const button = document.querySelector(".add-criterion button");
  if (model.available.length) {
    const ul = document.querySelector(".available-criterions ul");
    model.available.forEach(criterion => {
      ul.appendChild(newCriterionView(criterion));
    });
    button.disabled = false;
    button.title = "Add a new criterion";
  } else {
    button.disabled = true;
    button.title = "There are no new criterions to add";
  }
}

function newCriterionView(criterion) {
  const li = document.createElement("li");
  li.title = criterion.description;
  li.textContent = criterion.fullName;
  li.addEventListener("click", () => addCriterion(criterion.name));
  return li;
}

function toggleShowAddCriterion(event) {
  const div = event.currentTarget.parentNode;
  if (div.classList.contains("add-criterion__showing")) {
    div.classList.remove("add-criterion__showing");
  } else {
    if (model.available.length) {
      div.classList.add("add-criterion__showing");
    }
  }
}

/*************/
/* listeners */
/*************/

function initEventListeners() {
  initAddCriterionListeners();
}

function initAddCriterionListeners() {
  document
    .querySelector(".add-criterion button")
    .addEventListener("click", toggleShowAddCriterion);
}

/********/
/* init */
/********/

export function init(data) {
  initModel(data);
  view();
  initEventListeners();
}
