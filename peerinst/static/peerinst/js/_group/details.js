'use strict';

function removeAssignment(event, url) {
  event.stopPropagation();
  let li = event.currentTarget.parentNode.parentNode;
  let container = li.parentNode;

  let token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
  let req = {
    method: 'POST',
    headers: {
      'X-CSRFToken': token,
    },
  };
  url = url + 'remove/';

  fetch(url, req).then(function(resp) {
    if (resp.ok) {
      container.removeChild(li.nextSibling);
      container.removeChild(li);

      if (container.childNodes.length == 1) {
        location.reload();
      }
    }
  });
}

export {removeAssignment};
