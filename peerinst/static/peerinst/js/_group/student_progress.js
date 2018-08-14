'use strict';

import * as d3 from 'd3';
import {getStudentProgressData} from '../ajax.js';

function addStudentProgressView() {
  let url = document.querySelector('#student-progress');
  let data;
  getStudentProgressData(url)
    .then(function(d) {
      data = d;
    })
    .catch(function(err) {
      console.log(err);
      return;
    });

  let container = d3.select('#student-progress');

  container
    .selectAll('div')
    .data(data)
    .enter()
    .append('div');
}

export {addStudentProgressView};
