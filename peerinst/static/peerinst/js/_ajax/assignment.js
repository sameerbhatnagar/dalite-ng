async function getStudentProgressData(url) {
  let token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
  let req = {
    method: 'GET',
    headers: {
      'X-CSRFToken': token,
    },
  };
  let resp = await fetch(url, req);
  let data = await resp.json();
  return data;
}

export {getStudentProgressData};
