import { buildReq } from "../_ajax/utils.js";
import { clear } from "../utils.js";

/**********/
/* update */
/**********/

export function validateFormSubmit(event, url, quality) {
  event.preventDefault();
  const data = {
    quality: quality,
    rationale: document.querySelector("#id_rationale").value,
  };

  const req = buildReq(data, "post");
  fetch(url, req)
    .then(resp => resp.json())
    .then(json => {
      if (json.failed) {
        toggleQualityError(json.failed);
        document.querySelector("#answer-form").disabled = false;
      } else {
        toggleQualityError();
        document.querySelector("#answer-form").disabled = true;
        document.querySelector("#submit-answer-form").submit();
      }
    })
    .catch(err => console.log(err));
}

/********/
/* view */
/********/

function toggleQualityError(data) {
  if (data) {
    const form = document.querySelector("#submit-answer-form");

    let div = document.querySelector(".quality-error");
    if (!div) {
      div = document.createElement("div");
    }
    clear(div);

    div.classList.add("quality-error");
    div.textContent = "Your rationale didn't pass the following criterions: ";

    const ul = document.createElement("ul");
    div.append(ul);
    data.forEach(criterion => {
      const li = document.createElement("li");
      li.textContent = criterion.name;
      li.title = criterion.description;
      ul.append(li);
    });

    form.parentNode.insertBefore(div, form);
  } else {
    const err = document.querySelector("quality-error");
    if (err) {
      err.parentNode.removeChild(err);
    }
  }
}
