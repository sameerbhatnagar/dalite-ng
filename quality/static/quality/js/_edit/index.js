"use strict";

/*********/
/* model */
/*********/

let model;

function initModel(data) {
  model = {
    qualityType: data.quality_type,
    next: data.next,
    available: data.available.map(c => ({
      name: c.name,
      fullName: c.full_name,
      description: c.description,
    })),
  };
}

/**********/
/* update */
/**********/

function addCriterion(criterion) {}

/********/
/* view */
/********/

function view() {
  returnLinkView();
  newCriterionsView();
}

function returnLinkView() {
  const link = document.querySelector("#back-link");
  if (model.next) {
    link.href = model.next;
    link.textContent = `Back to ${model.qualityType}`;
  } else {
    link.parentNode.removeChild(link);
  }
}

function newCriterionsView() {
  const ul = document.querySelector(".available-criterions ul");
  model.available.forEach(criterion => {
    ul.appendChild(newCriterionView(criterion));
  });
}

function newCriterionView(criterion) {
  const li = document.createElement("li");
  li.title = criterion.description;
  li.textContent = criterion.fullName;
  li.addEventListener("click", addCriterion(criterion.name));
  return li;
}

function toggleShowAddCriterion(event) {
  const div = event.currentTarget.parentNode;
  if (div.classList.contains("add-criterion__showing")) {
    div.classList.remove("add-criterion__showing");
  } else {
    div.classList.add("add-criterion__showing");
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
  document.querySelectorAll(".add-criterion li").forEach(elem => {
    elem.addEventListener("click", () => addCriterion(elem));
  });
}

/********/
/* init */
/********/

export function init(data) {
  initModel(data);
  view();
  initEventListeners();
}
