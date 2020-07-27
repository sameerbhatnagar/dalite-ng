import { buildReq } from "../ajax.js";
/*********/
/* model */
/*********/

let model;

function initModel(urls) {
  model = {
    urls: {
      evaluateRationale: urls.evaluateRationale,
    },
  };
}

/**********/
/* update */
/**********/

function update() {
  updateRationalesEvaluationAttributes();
}

function updateRationalesEvaluationAttributes() {
  document
    .querySelectorAll(".custom-report__rationale")
    .forEach((rationale) => {
      updateRationaleEvaluationAttributes(rationale);
    });
}

function updateRationaleEvaluationAttributes(rationale) {
  const evaluation = rationale.getAttribute("data-score");
  if (evaluation != "") {
    const evaluation_ = parseInt(evaluation);
    if (evaluation_ == 0) {
      rationale.querySelector(".flag").setAttribute("data-flagged", "");
      rationale.querySelectorAll(".star").forEach((star, i) => {
        star.removeAttribute("data-starred");
      });
    } else {
      rationale.querySelector(".flag").removeAttribute("data-flagged");
      rationale.querySelectorAll(".star").forEach((star, i) => {
        if (3 - i <= evaluation_) {
          star.setAttribute("data-starred", "");
        } else {
          star.removeAttribute("data-starred");
        }
      });
    }
  }
}

async function flagRationale(flag) {
  const rationale = flag.parentNode.parentNode;
  const data = {
    answer: flag.parentNode.parentNode.getAttribute("data-id"),
    score: 0,
  };
  const req = buildReq(data, "post");

  const resp = await fetch(model.urls.evaluateRationale, req);
  if (resp.ok) {
    flag.setAttribute("data-flagged", "");
    rationale.setAttribute("data-score", "0");
  }
  updateRationaleEvaluationAttributes(rationale);
  rationaleEvaluationView();
}

async function evaluateRationale(star, score) {
  const rationale = star.parentNode.parentNode;
  const data = {
    answer: star.parentNode.parentNode.getAttribute("data-id"),
    score,
  };
  const req = buildReq(data, "post");

  const resp = await fetch(model.urls.evaluateRationale, req);
  if (resp.ok) {
    star.setAttribute("data-starred", "");
    rationale.setAttribute("data-score", `${score}`);
  }
  updateRationaleEvaluationAttributes(rationale);
  rationaleEvaluationView();
}

function handleFeedbackKeyDown(key, rationale, node) {
  if (key === "Enter") {
    saveFeedback(rationale, node);
  } else if (key === "Escape") {
    stopEditFeedback(rationale, node);
  }
}

function saveFeedback(rationale, node) {
  const url = model.urls.evaluateRationale;
  const input = node.querySelector("input");

  const data = {
    note: input.value,
    id: rationale.id,
  };

  const req = buildReq(data, "post");
  fetch(url, req)
    .then((resp) => resp.json())
    .then(function (data) {
      rationale.feedback = data.note;
      stopEditFeedback(rationale, node);
    })
    .catch(function (err) {
      stopEditFeedback(rationale, node);
      console.log(err);
    });
}

/********/
/* view */
/********/

function view() {
  rationaleEvaluationView();
}

function rationaleEvaluationView() {
  document
    .querySelectorAll(".custom-report__rationale__evaluation")
    .forEach((rationale) => {
      toggleFlagHover(rationale.querySelector(".flag"));
      rationale
        .querySelectorAll(".star")
        .forEach((star) => toggleStarHover(star));
    });

  document
    .querySelectorAll(".custom-report__rationale__feedback")
    .forEach((rationale) => {
      rationaleFeedbackView(rationale);
    });
}

function toggleFlagHover(flag, hovering = false) {
  if (hovering || flag.hasAttribute("data-flagged")) {
    flag.textContent = "flag";
  } else {
    flag.textContent = "outlined_flag";
  }
}

function toggleStarHover(star, hovering = false) {
  const stars = [...star.parentNode.getElementsByClassName("star")];
  const idx = stars.indexOf(star);
  stars.forEach((star, i) => {
    if (star.hasAttribute("data-starred") || (hovering && i >= idx)) {
      star.textContent = "star";
    } else {
      star.textContent = "star_border";
    }
  });
}

function rationaleFeedbackView(rationale) {
  const div = document.createElement("div");
  div.classList.add("student-group--id");

  const rationaleFeedback = document.createElement("span");
  rationaleFeedback.classList.add("student-group--id__id");
  rationaleFeedback.style.display = "inline-block";
  rationaleFeedback.textContent = rationale.feedback;
  rationaleFeedback.addEventListener("click", () =>
    editFeedback(rationale, div),
  );
  div.appendChild(rationaleFeedback);

  const input = document.createElement("input");
  input.classList.add("student-group--id__input");
  input.value = rationale.feedback;
  input.style.display = "none";
  input.addEventListener("keydown", (event) =>
    handleFeedbackKeyDown(event.key, rationale, div),
  );
  div.appendChild(input);

  const editIcon = document.createElement("i");
  editIcon.classList.add("material-icons", "md-28", "student-group--id__edit");
  editIcon.style.display = "flex";
  editIcon.textContent = "edit";
  editIcon.addEventListener("click", () => editFeedback(rationale, div));
  div.appendChild(editIcon);

  const confirmIcon = document.createElement("i");
  confirmIcon.classList.add(
    "material-icons",
    "md-28",
    "student-group--id__confirm",
  );
  confirmIcon.style.display = "none";
  confirmIcon.textContent = "check";
  confirmIcon.addEventListener("click", () => saveFeedback(rationale, div));
  div.appendChild(confirmIcon);

  const cancelIcon = document.createElement("i");
  cancelIcon.classList.add(
    "material-icons",
    "md-28",
    "student-group--id__cancel",
  );
  cancelIcon.style.display = "none";
  cancelIcon.textContent = "close";
  cancelIcon.addEventListener("click", () => stopEditFeedback(rationale, div));
  div.appendChild(cancelIcon);

  return div;
}

function editFeedback(rationale, node) {
  const span = node.querySelector(".student-group--id__id");
  const input = node.querySelector(".student-group--id__input");
  const copyBtn = node.querySelector(".student-group--id__copy");
  const editBtn = node.querySelector(".student-group--id__edit");
  const confirmBtn = node.querySelector(".student-group--id__confirm");
  const cancelBtn = node.querySelector(".student-group--id__cancel");

  input.value = rationale.feedback;

  span.style.display = "none";
  copyBtn.style.display = "none";
  editBtn.style.display = "none";
  input.style.display = "inline-block";
  confirmBtn.style.display = "flex";
  cancelBtn.style.display = "flex";

  input.focus();
}

function stopEditFeedback(rationale, node) {
  const span = node.querySelector("span");
  // const input = node.querySelector("input");
  const copyBtn = node.querySelector(".student-group--id__copy");
  const editBtn = node.querySelector(".student-group--id__edit");
  const confirmBtn = node.querySelector(".student-group--id__confirm");
  const cancelBtn = node.querySelector(".student-group--id__cancel");

  span.textContent = rationale.feedback;

  span.style.display = "inline-block";
  copyBtn.style.display = "flex";
  editBtn.style.display = "flex";
  // input.style.display = "none";
  confirmBtn.style.display = "none";
  cancelBtn.style.display = "none";
}

/*************/
/* listeners */
/*************/

function initListeners() {
  addFlagListeners();
  addEvaluateListeners();
}

function addFlagListeners() {
  document
    .querySelectorAll(".custom-report__rationale__evaluation .flag")
    .forEach((flag) => {
      flag.addEventListener("mouseenter", () => toggleFlagHover(flag, true));
      flag.addEventListener("mouseleave", () => toggleFlagHover(flag, false));
      flag.addEventListener("click", () => flagRationale(flag));
    });
}

function addEvaluateListeners() {
  document
    .querySelectorAll(".custom-report__rationale__evaluation")
    .forEach((rationale) => {
      rationale.querySelectorAll(".star").forEach((star, i) => {
        star.addEventListener("mouseenter", () => toggleStarHover(star, true));
        star.addEventListener("mouseleave", () =>
          toggleStarHover(star, false),
        );
        star.addEventListener("click", () => evaluateRationale(star, 3 - i));
      });
    });
}

/********/
/* init */
/********/

export function init(urls) {
  initModel(urls);
  update();
  view();
  initListeners();
}
