import { MDCSnackbar } from "@material/snackbar";

export function init(
  assignUrl,
  unassignUrl,
  assignTrans,
  unassignTrans,
  collectionTitle,
  youHaveAssign,
  toText,
  youHaveUnassign,
  fromCollToGroup,
  groupUrl,
) {
  const snackbar = new MDCSnackbar(document.querySelector(".mdc-snackbar"));

  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!bundle.csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", bundle.getCsrfToken());
      }
    },
  });

  function assignCollection(pk, ppk) {
    const posting = $.post(assignUrl, {
      pk: pk,
      ppk: ppk,
    });
    posting.done(function(data) {
      console.info(data);
    });
  }

  function unassignCollection(pk, ppk) {
    const posting = $.post(unassignUrl, {
      pk: pk,
      ppk: ppk,
    });
    posting.done(function(data) {
      console.info(data);
    });
  }

  function clickAssign(el) {
    assignCollection(el.getAttribute("id_pk"), el.getAttribute("id_ppk"));
    document.getElementById(
      el.getAttribute("id_pk"),
    ).innerHTML = unassignTrans;
    document.getElementById(el.getAttribute("id_pk")).classList.add("added");
    document
      .getElementById(el.getAttribute("id_pk"))
      .classList.remove("removed");
    const dataObjAssigned = {
      message:
        youHaveAssign + collectionTitle + toText + el.getAttribute("name"),
    };
    snackbar.show(dataObjAssigned);
  }

  function clickUnassign(el) {
    unassignCollection(el.getAttribute("id_pk"), el.getAttribute("id_ppk"));
    document.getElementById(el.getAttribute("id_pk")).innerHTML = assignTrans;
    document
      .getElementById(el.getAttribute("id_pk"))
      .classList.remove("added");
    document.getElementById(el.getAttribute("id_pk")).classList.add("removed");
    const dataObjUnassigned = {
      message:
        youHaveUnassign +
        collectionTitle +
        "'" +
        fromCollToGroup +
        el.getAttribute("name"),
    };
    snackbar.show(dataObjUnassigned);
  }

  [].forEach.call(
    document.querySelectorAll(".collection-toggle-assign"),
    el => {
      el.addEventListener("click", () => {
        if (el.classList.contains("removed")) {
          clickAssign(el);
        } else {
          clickUnassign(el);
        }
      });
    },
  );

  [].forEach.call(document.querySelectorAll(".md-48"), el => {
    el.addEventListener("click", () => {
      const hash = el.getAttribute("id");
      window.location.assign(groupUrl.replace("0", hash));
    });
  });
}
