// @flow

/*********/
/* model */
/*********/

let model: {
  submitAllowed: boolean,
};

function initModel() {
  model = {
    submitAllowed: false,
  };
}

/**********/
/* update */
/**********/

function startSubmitAllowedTimer(seconds: number) {
  setInterval(allowSubmit, seconds * 1000);
}

function allowSubmit() {
  model.submitAllowed = true;
  submitButtonView();
}

/********/
/* view */
/********/

function view() {
  submitButtonView();
}

function submitButtonView() {
  if (model.submitAllowed) {
    // $FlowFixMe
    document.getElementById("answer-form").disabled = false;
  } else {
    // $FlowFixMe
    document.getElementById("answer-form").disabled = true;
  }
}

function showMeMore() {
  [].forEach.call(document.querySelectorAll(".expand-button"), function (
    el,
    i,
  ) {
    el.addEventListener("click", function () {
      const els = document.getElementsByClassName(
        "hidden-" + el.getAttribute("data-rationale-iterator"),
      );
      const showCounter = document.getElementById(
        "show-counter-" + el.getAttribute("data-rationale-iterator"),
      );
      let shownCounter = 0;
      for (let i = 0; i < els.length; i++) {
        if (els[i].hidden == true && shownCounter < 2) {
          els[i].hidden = false;
          shownCounter++;
          if (i == els.length - 1) {
            el.hidden = true;
            break;
          }
          showCounter.setAttribute(
            "value",
            +showCounter.getAttribute("value") + 1,
          );
        }
      }
    });
  });
}

/********/
/* init */
/********/

export function init() {
  initModel();
  view();
  startSubmitAllowedTimer(5);
  showMeMore();
}
