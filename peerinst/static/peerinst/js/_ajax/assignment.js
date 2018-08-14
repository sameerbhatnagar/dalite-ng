async function getStudentProgressData(url) {
  let resp = await fetch(url);
  let data = await resp.json();
  return data;
}

export {getStudentProgressData};
