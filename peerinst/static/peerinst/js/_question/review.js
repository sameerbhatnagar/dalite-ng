/*********/
/* model */
/*********/

let model;

function initModel() {
  model = {
    submitAllowed: false,
  };
}

/**********/
/* update */
/**********/

function submitForm() {
  if (model.submitAllowed) {
    console.log("test");
    document.querySelector("#submit-answer-form").submit();
  } else {
    event.stopPropagation();
    showAlert();
  }
}

function startSubmitAllowedTimer(seconds) {
  setInterval(allowSubmit, seconds * 1000);
}

function allowSubmit() {
  model.submitAllowed = true;
}

/********/
/* view */
/********/

function showAlert() {
  document
    .querySelector("#review-alert")
    .classList.add("review-alert--showing");
}

function hideAlert() {
  document
    .querySelector("#review-alert")
    .classList.remove("review-alert--showing");
}

/*************/
/* listeners */
/*************/

function initListeners() {
  addSubmitListener();
  addAlertListeners();
}

function addSubmitListener() {
  document.querySelector("#answer-form").addEventListener("click", submitForm);
}

function addAlertListeners() {
  document.querySelector("#review-alert").addEventListener("click", event => {
    if (
      document
        .querySelector("#review-alert")
        .classList.contains("review-alert--showing")
    ) {
      event.stopPropagation();
      hideAlert();
    }
  });
  document.querySelector("#review-alert div").addEventListener("click", () => {
    event.stopPropagation();
  });
  document
    .querySelector("#review-alert button")
    .addEventListener("click", () => {
      hideAlert();
    });
  document.body.addEventListener("keydown", event => {
    if (
      event.key == "Escape" &&
      document
        .querySelector("#review-alert")
        .classList.contains("review-alert--showing")
    ) {
      event.stopPropagation();
      hideAlert();
    }
  });
}

/********/
/* init */
/********/

export function init() {
  initModel();
  initListeners();
  startSubmitAllowedTimer(2);
}
