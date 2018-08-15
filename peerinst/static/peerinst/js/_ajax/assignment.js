'use strict';

import {getCsrfToken} from './utils.js';

export async function getStudentProgressData(url) {
  let token = getCsrfToken();
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
