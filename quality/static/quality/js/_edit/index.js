"use strict";

import { buildReq } from "../../../../../peerinst/static/peerinst/js/_ajax/utils.js"; // eslint-disable-line
import { clear } from "../../../../../peerinst/static/peerinst/js/utils.js"; // eslint-disable-line
import { createInput } from "../utils.js";

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
      updateCriterion: data.urls.update_criterion,
      removeCriterion: data.urls.remove_criterion,
    },
  };
}

/**********/
/* update */
/**********/

function updateCriterionOption(criterion, option) {
  const data = {
    quality: model.quality.pk,
    criterion: criterion.name,
    field: option.name,
    value: option.value,
  };

  const req = buildReq(data, "post");
  fetch(model.urls.updateCriterion, req)
    .then(resp => {
      if (resp.ok) {
        return resp.json(), false;
      } else {
        return resp.text(), true;
      }
    })
    .then((data, err) => {
      if (err) {
        toggleCriterionOptionError(option, err);
      } else {
        criterion = data;
      }
    })
    .catch(err => console.log(err));
}

function addCriterion(criterion) {
  const data = {
    quality: model.quality.pk,
    criterion: criterion.name,
  };

  const req = buildReq(data, "post");
  fetch(model.urls.addCriterion, req)
    .then(resp => resp.json())
    .then(json => {
      model.criterions.push(json);
      criterionsView();
      newCriterionsView();
      toggleShowAddCriterion();
    })
    .catch(err => console.log(err));
}

function removeCriterion(criterion) {
  const data = {
    quality: model.quality.pk,
    criterion: criterion.name,
  };
  const req = buildReq(data, "post");
  fetch(model.urls.removeCriterion, req)
    .then(resp => {
      if (resp.ok) {
        model.criterions = model.criterions.filter(
          c => c.name != criterion.name,
        );
        criterionsView();
        newCriterionsView();
      }
    })
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
  clear(div);
  model.criterions.forEach(criterion => {
    div.appendChild(criterionView(criterion));
  });
}

function criterionView(criterion) {
  const div = document.createElement("div");
  div.classList.add("criterion");

  const name = document.createElement("div");
  name.classList.add("criterion--name");
  name.textContent = criterion.full_name;
  name.addEventListener("click", () => toggleCriterionOptions(div));
  div.appendChild(name);

  const remove = document.createElement("button");
  remove.classList.add("criterion--remove");
  remove.addEventListener("click", event => {
    removeCriterion(criterion);
    event.stopPropagation();
  });
  name.appendChild(remove);
  const icon = document.createElement("i");
  icon.classList.add("material-icons");
  icon.textContent = "close";
  remove.appendChild(icon);

  const options = document.createElement("div");
  options.classList.add("criterion--options");
  div.appendChild(options);

  // const versionLabel = document.createElement("label");
  // versionLabel.textContent = "Version:";
  // const version = document.createElement("select");
  // const versions = [document.createElement("option")];
  // versions[0].value = 0;
  // versions[0].textContent = "0 (latest)";
  // versions.forEach(v => {
  // version.appendChild(v);
  // });
  // options.appendChild(versionLabel);
  // options.appendChild(version);
  //
  const weightLabel = document.createElement("label");
  weightLabel.textContent = "Weight:";
  const weight = document.createElement("input");
  weight.name = "weight";
  weight.type = "number";
  weight.min = 0;
  weight.value = criterion.weight;
  weight.addEventListener("input", () =>
    updateCriterionOption(criterion, weight),
  );
  options.appendChild(weightLabel);
  options.appendChild(weight);

  const otherOptions = Object.keys(criterion).filter(
    o =>
      ![
        "description",
        "full_name",
        "is_beta",
        "name",
        "version",
        "versions",
        "weight",
      ].includes(o),
  );
  otherOptions.forEach(o => {
    const option = criterion[o];
    const label = document.createElement("label");
    label.textContent = `${option.full_name}:`;
    label.title = option.description;
    const input = createInput(option.type);
    input.name = option.name;
    input.value = option.value;
    input.addEventListener("input", () =>
      updateCriterionOption(criterion, input),
    );
    options.appendChild(label);
    options.appendChild(input);
  });

  return div;
}

function toggleCriterionOptions(criterion) {
  if (criterion.classList.contains("criterion__showing")) {
    criterion.classList.remove("criterion__showing");
  } else {
    criterion.classList.add("criterion__showing");
  }
}

function toggleCriterionOptionError(option) {}

function newCriterionsView() {
  const button = document.querySelector(".add-criterion button");
  const available = model.available.filter(
    c => !model.criterions.map(cc => cc.name).includes(c.name),
  );
  if (available.length) {
    const ul = document.querySelector(".available-criterions ul");
    clear(ul);
    available.forEach(criterion => {
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
  li.addEventListener("click", () => addCriterion(criterion));
  return li;
}

function toggleShowAddCriterion() {
  const div = document.querySelector(".add-criterion");
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
