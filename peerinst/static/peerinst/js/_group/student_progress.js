'use strict';

import * as d3 from 'd3';
import {getStudentProgressData} from '../ajax.js';

function addStudentProgressView() {
  let url = document
    .querySelector('#student-progress')
    .getAttribute('data-url');
  getStudentProgressData(url)
    .then(function(data) {
      studentProgressView(data);
    })
    .catch(function(err) {
      console.log(err);
      return;
    });
}

function toggleStudentProgressView() {
  let showing =
    document.querySelector('#student-progress').getAttribute('data-showing') ===
    'true';
  if (showing) {
  } else {
  }
}

function studentProgressView(data) {
  let ul = document.querySelector('#student-progress');
  data.forEach(function(question) {
    ul.append(questionView(question));
  });
}

function questionView(data) {
  let li = document.createElement('li');
  li.classList.add('mdc-list-item');

  let image = document.createElement('span');
  image.classList.add('mdc-list-item__graphic', 'mdc-theme--primary');
  let i = document.createElement('i');
  i.classList.add('mdc-theme--primary', 'material-icons', 'md-48');
  i.textContent = 'question_answer';
  image.append(i);
  li.append(image);

  let title = document.createElement('span');
  title.classList.add('mdc-list-item__text', 'mdc-theme--secondary', 'bold');
  title.textContent = data.question_title;
  let nStudents = document.createElement('span');
  nStudents.classList.add('mdc-list-item__secondary-text');
  nStudents.textContent = data.students.length + ' students';
  title.append(nStudents);
  li.append(title);

  let progress = document.createElement('span');
  progress.classList.add('mdc-list-item__meta');
  li.append(progress);

  let width = 72;
  let height = 72;

  progressView(
    progress,
    data['first'],
    data['students'].length,
    'First answer done',
    height,
    width,
  );
  progressView(
    progress,
    data['second'],
    data['students'].length,
    'Second answer done',
    height,
    width,
  );
  correctView(
    progress,
    data['first_correct'],
    data['students'].length,
    'First answer correct',
    height,
    width,
  );
  correctView(
    progress,
    data['second_correct'],
    data['students'].length,
    'Second answer correct',
    height,
    width,
  );

  return li;
}

function progressView(
  container,
  data,
  total,
  name,
  height,
  width,
  reverse = false,
) {
  let radius = Math.min(width, height) / 2;

  let startAngle;
  let endAngle;
  if (reverse) {
    startAngle = 2 * Math.PI;
    endAngle = 0;
  } else {
    startAngle = 0;
    endAngle = 2 * Math.PI;
  }

  // let pie = d3
  // .pie()
  // .value(d => d)
  // .sort(null);

  let colours = ['--mdc-theme-primary', '#ffffff'];

  let svg = d3
    .select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', 'translate(' + width / 2 + ',' + height / 2 + ')');

  let arc = d3
    .arc()
    .innerRadius(radius - 10)
    .outerRadius(radius)
    .startAngle(startAngle)
    .endAngle(endAngle);

  let arcLine = d3
    .arc()
    .innerRadius(radius - 10)
    .outerRadius(radius)
    .startAngle(startAngle);

  svg
    .append('path')
    .attr('d', arc)
    .style('fill', colours[1]);

  let pathChart = svg
    .append('path')
    .datum({endAngle: endAngle})
    .attr('d', arcLine)
    .style('fill', colours[0]);

  let count = svg
    .append('text')
    .text(d => d)
    .attr('text-anchor', 'middle')
    // .attr('dy', 30)
    // .attr('dx', -15)
    .style('fill', colours[0])
    .attr('font-size', '90px');

  let arcTween = function(transition, newAngle_) {
    transition.attrTween('d', function(d) {
      let interpolate = d3.interpolate(d.endAngle, newAngle_);
      let interpolateCount = d3.interpolate(0, data);
      return function(t) {
        d.endAngle = interpolate(t);
        count.text(Math.floor(interpolateCount(t)));
        return arcLine(d);
      };
    });
  };

  let animate = function() {
    pathChart
      .transition()
      .duration(750)
      .ease('cubic')
      .call(arcTween, (2 * Math.PI * data) / total);
  };

  // setTimeout(animate, 0);

  return svg;
}

function correctView(container, data, name, total, height, width) {
  let radius = Math.min(width, height) / 2;

  let svg = d3
    .select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height);

  return svg;
}

export {addStudentProgressView};
