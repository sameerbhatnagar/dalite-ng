'use strict';

import * as d3 from 'd3';
import {getStudentProgressData} from '../ajax.js';

export function addStudentProgressView() {
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

export function toggleStudentProgressView() {
  let ul = document.querySelector('#student-progress');
  let showing = ul.getAttribute('data-showing') === 'true';

  let completes = ul.querySelectorAll('.student-progress-complete');
  let corrects = ul.querySelectorAll('.student-progress-correct');

  completes.forEach(function(svg) {
    animateComplete(svg, showing);
  });
  corrects.forEach(function(svg) {
    animateCorrect(svg, showing);
  });

  ul.setAttribute('data-showing', !showing);
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

  let width = 62;
  let height = 48;
  let total = data['students'].length;

  completeView(progress, data['first'], total, height, width);
  completeView(progress, data['second'], total, height, width);
  correctView(progress, data['first_correct'], total, height, width);
  correctView(progress, data['second_correct'], total, height, width);

  return li;
}

function completeView(container, data, total, height, width) {
  let radius = Math.min(width, height) / 2;

  let svg = d3
    .select(container)
    .append('svg')
    .attr('class', 'student-progress-complete')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', 'translate(' + width / 2 + ',' + height / 2 + ')');

  let arcBackground = d3
    .arc()
    .innerRadius(radius - 5)
    .outerRadius(radius)
    .startAngle(0)
    .endAngle(2 * Math.PI);

  let arcData = d3
    .arc()
    .innerRadius(radius - 5)
    .outerRadius(radius)
    .startAngle(0);

  svg
    .append('path')
    .attr('d', arcBackground)
    .attr('class', 'fill-primary')
    .style('opacity', '0.10');

  svg
    .append('path')
    .datum({endAngle: 0})
    .attr('d', arcData)
    .attr('class', 'fill-primary student-progress__path');

  svg
    .append('text')
    .attr('data-count', data)
    .attr('data-total', total)
    .text(0)
    .attr('text-anchor', 'middle')
    .attr('dy', 8)
    .attr('class', 'fill-primary student-progress__count')
    .attr('font-size', '20px');

  return svg;
}

function correctView(container, data, total, height, width) {
  let radius = Math.min(width, height) / 2;

  let svg = d3
    .select(container)
    .append('svg')
    .attr('class', 'student-progress-correct')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', 'translate(' + width / 2 + ',' + height / 2 + ')');

  let colourScale = d3
    .scaleQuantile()
    .domain([0, 1])
    .range(['#b30000', '#f17f4d', '#339966']);

  let arcBackground = d3
    .arc()
    .innerRadius(radius - 5)
    .outerRadius(radius)
    .startAngle(0)
    .endAngle(2 * Math.PI);

  let arcData = d3
    .arc()
    .innerRadius(radius - 5)
    .outerRadius(radius)
    .startAngle(0);

  svg
    .append('path')
    .attr('d', arcBackground)
    .attr('class', 'fill-primary')
    .style('opacity', '0.10');

  svg
    .append('path')
    .datum({endAngle: 0})
    .attr('d', arcData)
    .style('fill', colourScale(0))
    .attr('class', 'student-progress__path');

  svg
    .append('text')
    .attr('data-count', data)
    .attr('data-total', total)
    .text(0)
    .attr('text-anchor', 'middle')
    .attr('dy', 8)
    .style('fill', colourScale(0))
    .attr('font-size', '24px')
    .attr('class', 'student-progress__count');

  return svg;
}

function animateComplete(svg, reverse = false) {
  let path_ = svg.querySelector('.student-progress__path');
  let count_ = svg.querySelector('.student-progress__count');
  let data = count_.getAttribute('data-count');
  let total = count_.getAttribute('data-total');

  let start;
  let end;
  if (reverse) {
    start = data;
    end = 0;
  } else {
    start = 0;
    end = data;
  }

  let width = svg.getAttribute('width');
  let height = svg.getAttribute('height');
  let radius = Math.min(width, height) / 2;

  let arcData = d3
    .arc()
    .innerRadius(radius - 5)
    .outerRadius(radius)
    .startAngle(0);

  let path = d3
    .select(path_)
    .attr('d', arcData);

  let count = d3.select(count_);

  function animation(transition, newAngle) {
    transition.attrTween('d', function(d) {
      let interpolate = d3.interpolate(d.endAngle, newAngle);
      let interpolateCount = d3.interpolate(start, end);
      return function(t) {
        d.endAngle = interpolate(t);
        count.text(Math.floor(interpolateCount(t)));
        return arcData(d);
      };
    });
  }

  function animate() {
    path
      .transition()
      .delay(500*Math.random())
      .duration(2000)
      .ease(d3.easeCubicInOut)
      .call(animation, (2 * Math.PI * end) / total);
  }

  setTimeout(animate, 0);
}

function animateCorrect(svg, reverse = false) {
  let path_ = svg.querySelector('.student-progress__path');
  let count_ = svg.querySelector('.student-progress__count');
  let data = count_.getAttribute('data-count');
  let total = count_.getAttribute('data-total');

  let colourScale = d3
    .scaleQuantile()
    .domain([0, 1])
    .range(['#b30000', '#f17f4d', '#339966']);

  let start;
  let end;
  if (reverse) {
    start = data;
    end = 0;
  } else {
    start = 0;
    end = data;
  }

  let width = svg.getAttribute('width');
  let height = svg.getAttribute('height');
  let radius = Math.min(width, height) / 2;

  let arcData = d3
    .arc()
    .innerRadius(radius - 5)
    .outerRadius(radius)
    .startAngle(0);

  let path = d3
    .select(path_)
    .attr('d', arcData);

  let count = d3.select(count_);

  function animation(transition, newAngle) {
    transition.attrTween('d', function(d) {
      let interpolate = d3.interpolate(d.endAngle, newAngle);
      let interpolateCount = d3.interpolate(start, end);
      return function(t) {
        d.endAngle = interpolate(t);
        let newCount = interpolateCount(t);
        path.style('fill', colourScale(newCount / total));
        count.text(Math.floor(newCount));
        count.style('fill', colourScale(newCount / total));
        return arcData(d);
      };
    });
  }

  function animate() {
    path
      .transition()
      .delay(500*Math.random())
      .duration(2000)
      .ease(d3.easeCubicInOut)
      .call(animation, (2 * Math.PI * end) / total);
  }

  setTimeout(animate, 0);
}
