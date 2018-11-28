"use strict";
import flatpickr from "flatpickr";

function editField(event, type, className) {
  let iconContainer = event.currentTarget.parentNode.parentNode;
  let container = event.currentTarget.parentNode.previousElementSibling;
  let field =
    event.currentTarget.parentNode.previousElementSibling.firstElementChild;

  let newField;

  if (type == "text") {
    newField = editTextField(field);
  } else if (type == "textList") {
    newField = editTextListField(field);
  } else if (type == "datetime") {
    newField = editDateTimeField(field);
  } else {
    console.log(
      "The `editField` function isn 't implemented for type " + type + ".",
    );
    return;
  }

  container.replaceChild(newField, field);

  let iconsDiv = event.currentTarget.parentNode;
  let newIconsDiv = iconsDiv.cloneNode(false);

  newIconsDiv = toggleIcons(newIconsDiv, type, false, className);

  iconContainer.replaceChild(newIconsDiv, iconsDiv);
}

function saveField(event, type, save, className) {
  let iconContainer = event.currentTarget.parentNode.parentNode;
  let container = event.currentTarget.parentNode.previousElementSibling;
  let field =
    event.currentTarget.parentNode.previousElementSibling.firstElementChild;
  let url = container.parentNode.parentNode.parentNode.getAttribute(
    "data-update-url",
  );
  if (type == "text") {
    saveTextField(field, save, className, url).then(function(newField) {
      container.replaceChild(newField, field);
    });
  } else if (type == "textList") {
    saveTextListField(field, save, className, url).then(function(newField) {
      container.replaceChild(newField, field);
    });
  } else if (type == "datetime") {
    saveDateTimeField(field, save, className, url).then(function(newField) {
      container.replaceChild(newField, field);
    });
  } else {
    console.log(
      "The `saveField` function isn't implemented for type " + type + ".",
    );
    return;
  }

  let iconsDiv = event.currentTarget.parentNode;
  let newIconsDiv = iconsDiv.cloneNode(false);

  newIconsDiv = toggleIcons(newIconsDiv, type, true, className);

  iconContainer.replaceChild(newIconsDiv, iconsDiv);
}

function editTextField(field) {
  let newField = document.createElement("div");
  let name = field.getAttribute("name");
  newField.setAttribute("name", name);
  let input = document.createElement("input");
  input.type = "text";
  input.value = field.textContent;
  input.setAttribute("data-old-content", field.textContent);
  newField.append(input);
  return newField;
}

function editTextListField(field) {
  let newField = document.createElement("div");
  let name = field.getAttribute("name");
  newField.setAttribute("name", name);
  let ul = field.childNodes[0].cloneNode(true);
  let li_ = document.createElement("li");
  let input = document.createElement("input");
  input.type = "text";
  input.value = "";
  input.setAttribute("data-old-content", "");
  li_.append(input);
  ul.append(li_);

  newField.append(ul);
  return newField;
}

function editDateTimeField(field) {
  let newField = document.createElement("div");
  let name = field.getAttribute("name");
  newField.setAttribute("name", name);
  let input = document.createElement("input");
  input.type = "text";
  input.setAttribute("data-old-content", field.textContent);
  newField.append(input);
  let datetime = field.textContent
    .match(/(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})/)
    .slice(1)
    .map(x => parseInt(x));
  datetime[1] -= 1;
  flatpickr(input, {
    enableTime: true,
    defaultDate: new Date(...datetime),
    dateFormat: "Z",
    altInput: true,
    altFormat: "Y-m-d H:i",
    minDate: "today",
  });
  return newField;
}

function toggleIcons(newIconsDiv, type, toEdit, className) {
  if (toEdit) {
    let editIcon = document.createElement("i");
    editIcon.classList.add(
      "material-icons",
      "md-24",
      "mdc-ripple-surface",
      "icon-list",
    );
    if ((type == "text") | (type == "datetime")) {
      editIcon.textContent = "edit";
      editIcon.title = "Edit";
    } else {
      editIcon.textContent = "add";
      editIcon.title = "Add";
    }
    editIcon.setAttribute(
      "onclick",
      'bundle.editField(event, "' + type + '", "' + className + '")',
    );
    newIconsDiv.append(editIcon);
  } else {
    let saveIcon = document.createElement("i");
    saveIcon.classList.add(
      "material-icons",
      "md-24",
      "mdc-ripple-surface",
      "icon-list",
    );
    saveIcon.textContent = "check";
    saveIcon.title = "Save";
    saveIcon.setAttribute(
      "onclick",
      'bundle.saveField(event, "' + type + '", true, "' + className + '")',
    );
    let cancelIcon = document.createElement("i");
    cancelIcon.classList.add(
      "material-icons",
      "md-24",
      "mdc-ripple-surface",
      "icon-list",
    );
    cancelIcon.textContent = "close";
    cancelIcon.title = "Cancel";
    cancelIcon.setAttribute(
      "onclick",
      'bundle.saveField(event, "' + type + '", false, "' + className + '")',
    );
    newIconsDiv.append(saveIcon);
    newIconsDiv.append(cancelIcon);
  }

  return newIconsDiv;
}

async function saveTextField(field, save, className, url) {
  let newField = document.createElement("span");
  let name = field.getAttribute("name");
  newField.setAttribute("name", name);
  newField.setAttribute("class", className);
  if (save) {
    let newValue = field.firstChild.value;
    let err = await updateDetails(name, newValue, url);
    if (err) {
      newField.textContent = field.firstChild.getAttribute("data-old-content");
    } else {
      newField.textContent = newValue;
    }
  } else {
    newField.textContent = field.firstChild.getAttribute("data-old-content");
  }
  return newField;
}

async function saveTextListField(field, save, className, url) {
  let newField = document.createElement("span");
  let name = field.getAttribute("name");
  newField.setAttribute("name", name);
  let ul = field.firstChild.cloneNode(true);
  let li = field.firstChild.lastChild;
  ul.removeChild(ul.lastChild);
  if (save) {
    let newValue = li.firstChild.value;
    let err = await updateDetails(name, newValue, url);
    if (!err) {
      let li_ = document.createElement("li");
      li_.textContent = newValue;
      li_.setAttribute("class", className);
      ul.append(li_);
    }
  }
  newField.append(ul);
  return newField;
}

async function saveDateTimeField(field, save, className, url) {
  let newField = document.createElement("span");
  let name = field.getAttribute("name");
  newField.setAttribute("name", name);
  newField.setAttribute("class", className);
  if (save) {
    let sentValue = field.firstChild.value;
    let newValue = flatpickr.formatDate(new Date(sentValue), "Y-m-d H:i");
    let err = await updateDetails(name, sentValue, url);
    if (err) {
      newField.textContent = field.firstChild.getAttribute("data-old-content");
    } else {
      newField.textContent = newValue;
    }
  } else {
    newField.textContent = field.firstChild.getAttribute("data-old-content");
  }
  return newField;
}

async function updateDetails(name, value, url) {
  let data = { name: name, value: value };
  let token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
  let req = {
    method: "POST",
    body: JSON.stringify(data),
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": token,
    },
  };

  let resp = await fetch(url, req);
  let err = await resp.text();

  return err;
}

export { editField, saveField };
