function editField(event, type) {
  let container = event.currentTarget.parentNode.parentNode;

  let field = event.currentTarget.parentNode.previousSibling;
  let newField;

  if (type == 'text') {
    newField = editTextField(field);
  } else if (type == 'datetime') {
    newField = editDatetimeField(field);
  } else if (type == 'textList') {
    newField = editTextListField(field);
  } else {
    console.log(
      "The `editField` function isn 't implemented for type " + type + '.',
    );
    return;
  }

  container.replaceChild(newField, field);

  let iconsDiv = event.currentTarget.parentNode;
  let newIconsDiv = iconsDiv.cloneNode(false);

  newIconsDiv = toggleIcons(newIconsDiv, type, false);

  container.replaceChild(newIconsDiv, iconsDiv);
}

function saveField(event, type, save) {
  let container = event.currentTarget.parentNode.parentNode;

  let field = event.currentTarget.parentNode.previousSibling;
  let newField;

  if (type == 'text') {
    newField = saveTextDateTimeField(field, save);
  } else if (type == 'datetime') {
    newField = saveTextDateTimeField(field, save);
  } else if (type == 'textList') {
    newField = saveTextListField(field, save);
  } else {
    console.log(
      "The `saveField` function isn't implemented for type " + type + '.',
    );
    return;
  }

  container.replaceChild(newField, field);

  let iconsDiv = event.currentTarget.parentNode;
  let newIconsDiv = iconsDiv.cloneNode(false);

  newIconsDiv = toggleIcons(newIconsDiv, type, true);

  container.replaceChild(newIconsDiv, iconsDiv);
}

function editTextField(field) {
  let newField = document.createElement('div');
  let name = field.name;
  newField.name = name;
  let input = document.createElement('input');
  input.type = 'text';
  input.value = field.textContent;
  input.setAttribute('data-old-content', field.textContent);
  newField.append(input);
  return newField;
}

function editDatetimeField(field) {
  let newField = document.createElement('div');
  let name = field.name;
  newField.name = name;
  let input = document.createElement('input');
  input.type = 'text';
  input.classList.add('flatpickr-input', 'active');
  input.readonly = 'readonly';
  input.value = field.textContent;
  input.setAttribute('data-old-content', field.textContent);
  newField.append(input);
  return newField;
}

function saveTextDateTimeField(field, save) {
  let newField = document.createElement('div');
  let name = field.name;
  newField.name = name;
  if (save) {
    let newValue = field.childNodes[0].value;
    err = updateDetails(name, newValue);
    if (err) {
      newField.textContent = field.childNodes[0].getAttribute(
        'data-old-content',
      );
    } else {
      newField.textContent = newValue;
    }
  } else {
    newField.textContent = field.childNodes[0].getAttribute('data-old-content');
  }
  return newField;
}

function editTextListField(field) {
  let newField = document.createElement('div');
  let name = field.name;
  newField.name = name;
  let ul = field.childNodes[0].cloneNode(true);
  let li_ = document.createElement('li');
  let input = document.createElement('input');
  input.type = 'text';
  input.value = '';
  input.setAttribute('data-old-content', '');
  li_.append(input);
  ul.append(li_);

  newField.append(ul);
  return newField;
}

function saveTextListField(field, save) {
  let newField = document.createElement('div');
  let name = field.name;
  newField.name = name;
  let ul = field.firstChild.cloneNode(false);
  let li = field.firstChild.childNodes;
  if (save) {
    let newValue = [];
    for (let i = 0; i < li.length; i++) {
      if (i < li.length - 1) {
        newValue.push(li[i].textContent);
      } else if (li[i].firstChild.value) {
        newValue.push(li[i].firstChild.value);
      }
    }
    let err = updateDetails(name, newValue);
    console.log(err);
    if (err) {
      for (let i = 0; i < li.length; i++) {
        let li_ = document.createElement('li');
        li_.textContent = li[i].firstChild.getAttribute('data-old-content');
        if (li_.textContent) {
          ul.append(li_);
        }
      }
    } else {
      for (let i = 0; i < newValue.length; i++) {
        let li_ = document.createElement('li');
        li_.textContent = newValue[i];
        ul.append(li_);
      }
    }
  } else {
    for (let i = 0; i < li.length - 1; i++) {
      let li_ = li[i].cloneNode(true);
      ul.append(li_);
    }
  }
  newField.append(ul);
  return newField;
}

function toggleIcons(newIconsDiv, type, toEdit) {
  if (toEdit) {
    let editIcon = document.createElement('i');
    editIcon.classList.add(
      'material-icons',
      'md-24',
      'mdc-ripple-surface',
      'icon-list',
    );
    editIcon.textContent = 'edit';
    editIcon.title = 'Edit';
    editIcon.setAttribute('onclick', 'bundle.editField(event, "' + type + '")');
    newIconsDiv.append(editIcon);
  } else {
    let saveIcon = document.createElement('i');
    saveIcon.classList.add(
      'material-icons',
      'md-24',
      'mdc-ripple-surface',
      'icon-list',
    );
    saveIcon.textContent = 'check';
    saveIcon.title = 'Save';
    saveIcon.setAttribute(
      'onclick',
      'bundle.saveField(event, "' + type + '", true)',
    );
    let cancelIcon = document.createElement('i');
    cancelIcon.classList.add(
      'material-icons',
      'md-24',
      'mdc-ripple-surface',
      'icon-list',
    );
    cancelIcon.textContent = 'close';
    cancelIcon.title = 'Cancel';
    cancelIcon.setAttribute(
      'onclick',
      'bundle.saveField(event, "' + type + '", false)',
    );
    newIconsDiv.append(saveIcon);
    newIconsDiv.append(cancelIcon);
  }

  return newIconsDiv;
}

function updateDetails(name, value) {
  let data = {name: name, value: value};
  let token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
  let req = {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': token,
    },
  };
  let url = document
    .getElementById('group-details')
    .getAttribute('data-group-update-url');
  fetch(url, req)
    .then(resp => resp.text())
    .then(function(err) {
      console.log(err);
      return err;
    })
    .catch(function(err) {
      console.log(err);
      return err;
    });
}

export {editField, saveField};
