// MDC
import autoInit from '@material/auto-init/index';
import * as checkbox from '@material/checkbox/index';
import * as chips from '@material/chips/index';
import * as dialog from '@material/dialog/index';
import * as drawer from '@material/drawer/index';
import * as iconToggle from '@material/icon-toggle/index';
import * as radio from '@material/radio/index';
import * as ripple from '@material/ripple/index';
import * as selectbox from '@material/select/index';
import * as textField from '@material/textfield/index';
import * as toolbar from '@material/toolbar/index';

autoInit.register('MDCCheckbox', checkbox.MDCCheckbox);
autoInit.register('MDCChip', chips.MDCChip);
autoInit.register('MDCChipSet', chips.MDCChipSet);
autoInit.register('MDCDialog', dialog.MDCDialog);
autoInit.register('MDCDrawer', drawer.MDCTemporaryDrawer);
autoInit.register('MDCIconToggle', iconToggle.MDCIconToggle);
autoInit.register('MDCRadio', radio.MDCRadio);
autoInit.register('MDCRipple', ripple.MDCRipple);
autoInit.register('MDCSelect', selectbox.MDCSelect);
autoInit.register('MDCTextField', textField.MDCTextField);
autoInit.register('MDCToolbar', toolbar.MDCToolbar);

export {
  autoInit,
  checkbox,
  chips,
  dialog,
  drawer,
  iconToggle,
  radio,
  ripple,
  selectbox,
  textField,
  toolbar,
};

// D3
import * as d3 from 'd3';

export {
  active,
  area,
  axisBottom,
  axisLeft,
  curveNatural,
  entries,
  format,
  interrupt,
  keys,
  line,
  now,
  path,
  range,
  rgb,
  scaleBand,
  scaleLinear,
  scaleOrdinal,
  select,
  selectAll,
  transition,
  values,
} from 'd3';

// Custom functions (works with utils.scss)
import {addEventListeners} from './utils';

addEventListeners();

// Ajax
/** Define csrf safe HTTP methods
 *   https://docs.djangoproject.com/en/1.8/ref/csrf/
 * @function
 * @param {String} method
 * @return {Boolean}
 */
export function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
}

/** Get csrf token using jQuery
 *   https://docs.djangoproject.com/en/1.8/ref/csrf/
 * @function
 * @param {String} name
 * @return {String}
 */
export function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie != '') {
    let cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      let cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) == name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/** Replace element with text input form using Ajax
 * @function
 * @param {String} idToBind
 * @param {String} formToReplace
 * @param {String} url
 */
export function bindAjaxTextInputForm(idToBind, formToReplace, url) {
  let d = document.getElementById(idToBind);
  if (d) {
    d.onclick = function() {
      /** The callback
       * @function
       * @this Callback
       */
      function callback() {
        bundle.autoInit();
        let input = this.querySelector('.mdc-text-field__input');
        input.focus();
      }
      $('#' + formToReplace).load(url, callback);
    };
  }
}

// Custom functions
/** Corner language switcher
 * @function
 * @param {String} svgSelector
 * @param {String} formID
 * @param {String} lang
 * @param {String} className
 */
export function cornerGraphic(svgSelector, formID, lang, className) {
  let svg = d3.select(svgSelector);
  let w = +svg.attr('width');
  let h = +svg.attr('height');

  const g = svg.append('g');
  g.append('path')
    .attr('class', className)
    .attr('d', () => {
      let path = d3.path();
      path.moveTo(0, h);
      path.lineTo(w, 0);
      path.lineTo(w, h);
      path.closePath();
      return path;
    });

  g.append('text')
    .attr('x', w - w / 3)
    .attr('y', h - h / 3 + h / 6)
    .attr('text-anchor', 'middle')
    .style('fill', 'white')
    .style('font-size', h / 3 + 'px')
    .text(lang);

  g.on('click', () => {
    document.getElementById(formID).submit();
  });
}

/** Mike Bostock's svg line wrap function
 *   https://bl.ocks.org/mbostock/7555321
 *   (only slightly modified)
 * @function
 * @param {String} text
 * @param {Int} width
 * @this Wrap
 */
export function wrap(text, width) {
  text.each(
    /* @this */ function() {
      let text = bundle.select(this);
      let words = text
        .text()
        .split(/\s+/)
        .reverse();
      let word;
      let line = [];
      let lineNumber = 0;
      let lineHeight = 16; // px
      let x = text.attr('x');
      let dx = text.attr('dx');
      let y = text.attr('y');
      let dy = parseFloat(text.attr('dy'));
      let tspan = text
        .text(null)
        .append('tspan')
        .attr('x', x)
        .attr('y', y)
        .attr('dx', dx)
        .attr('dy', dy + 'px');
      while ((word = words.pop())) {
        line.push(word);
        tspan.text(line.join(' '));
        if (tspan.node().getComputedTextLength() > width) {
          line.pop();
          tspan.text(line.join(' '));
          line = [word];
          tspan = text
            .append('tspan')
            .attr('x', x)
            .attr('y', y)
            .attr('dx', dx)
            .attr('dy', ++lineNumber * lineHeight + dy + 'px')
            .text(word);
        }
      }
    },
  );
}


/** Underline h1 with svg
 *  @function
 */
function underlines() {
  'use strict';

  // Decorate h1 headers
  let lines = d3.selectAll('.underline');
  lines.selectAll('g').remove();
  let w = document.querySelector('main').offsetWidth;

  let gradientX = lines
    .append('linearGradient')
    .attr('id', 'underlineGradientX')
    .attr('x1', 0)
    .attr('x2', 1)
    .attr('y1', 0)
    .attr('y2', 0);

  gradientX
    .append('stop')
    .attr('offset', '0%')
    .attr('stop-color', '#54c0db');

  gradientX
    .append('stop')
    .attr('offset', '100%')
    .attr('stop-color', '#004266');

  let gradientY = lines
    .append('linearGradient')
    .attr('id', 'underlineGradientY')
    .attr('x1', 0)
    .attr('x2', 0)
    .attr('y1', 0)
    .attr('y2', 1);

  gradientY
    .append('stop')
    .attr('offset', '0%')
    .attr('stop-color', '#004266');

  gradientY
    .append('stop')
    .attr('offset', '100%')
    .attr('stop-color', '#54c0db');

  let g = lines.append('g');
  g.append('rect')
    .attr('x', -10)
    .attr('y', 0)
    .attr('width', w + 10)
    .attr('height', 1)
    .attr('fill', 'url(#underlineGradientX)');

  g.append('rect')
    .attr('x', w)
    .attr('y', 0)
    .attr('width', 1)
    .attr('height', 120)
    .attr('fill', 'url(#underlineGradientY)');
}


/** Question difficulty
 *  @function
 *  @param {Object} matrix
 *  @param {string} id
 */
export function difficulty(matrix, id) {
  matrix = JSON.parse(matrix);
  const colour = {
    easy: 'rgb(30, 142, 62)',
    hard: 'rgb(237, 69, 40)',
    tricky: 'rgb(237, 170, 30)',
    peer: 'rgb(25, 118, 188)',
  };
  let max = -0;
  let label = '';
  for (let entry in bundle.entries(matrix)) {
    if ({}.hasOwnProperty.call(bundle.entries(matrix), entry)) {
      let item = bundle.entries(matrix)[entry];
      if (item.value > max) {
        max = item.value;
        label = item.key;
      }
    }
  }
  if (max > 0) {
    const rating = document.getElementById('rating-' + id);
    rating.innerHTML = label.substring(0, 1).toUpperCase() + label.substring(1);

    const stats = document.getElementById('stats-' + id);
    stats.style.color = colour[label];
  }
}


/** Question analytics
 *  @function
 *  @param {Object} matrix
 *  @param {Object} freq
 *  @param {string} id
 */
export function plot(matrix, freq, id) {
  const colour = {
    easy: 'rgb(30, 142, 62)',
    hard: 'rgb(237, 69, 40)',
    tricky: 'rgb(237, 170, 30)',
    peer: 'rgb(25, 118, 188)',
  };
  let max = -0;
  let label = '';
  for (let entry in bundle.entries(matrix)) {
    if ({}.hasOwnProperty.call(bundle.entries(matrix), entry)) {
      let item = bundle.entries(matrix)[entry];
      if (item.value > max) {
        max = item.value;
        label = item.key;
      }
    }
  }
  if (max > 0) {
    const rating = document.getElementById('rating-' + id);
    rating.innerHTML = label.substring(0, 1).toUpperCase() + label.substring(1);

    const stats = document.getElementById('stats-' + id);
    stats.style.color = colour[label];
  }

  const matrixSvg = bundle.select('#matrix-' + id);
  let size = matrixSvg.attr('width');
  const g = matrixSvg.append('g');

  g.append('rect')
    .attr('x', 0)
    .attr('y', 0)
    .attr('width', size / 2)
    .attr('height', size / 2)
    .attr('fill', colour['easy'])
    .style('opacity', 0.5 + 0.5 * matrix['easy']);

  g.append('text')
    .attr('x', size / 4)
    .attr('y', size / 4)
    .attr('dy', 4)
    .style('font-size', '8pt')
    .style('fill', 'white')
    .style('text-anchor', 'middle')
    .text(parseInt(100 * matrix['easy']) + '%');

  g.append('rect')
    .attr('x', size / 2)
    .attr('y', size / 2)
    .attr('width', size / 2)
    .attr('height', size / 2)
    .attr('fill', colour['hard'])
    .style('opacity', 0.5 + 0.5 * matrix['hard']);

  g.append('text')
    .attr('x', (3 * size) / 4)
    .attr('y', (3 * size) / 4)
    .attr('dy', 4)
    .style('font-size', '8pt')
    .style('fill', 'white')
    .style('text-anchor', 'middle')
    .text(parseInt(100 * matrix['hard']) + '%');

  g.append('rect')
    .attr('x', 0)
    .attr('y', size / 2)
    .attr('width', size / 2)
    .attr('height', size / 2)
    .attr('fill', colour['peer'])
    .style('opacity', 0.5 + 0.5 * matrix['peer']);

  g.append('text')
    .attr('x', size / 4)
    .attr('y', (3 * size) / 4)
    .attr('dy', 4)
    .style('font-size', '8pt')
    .style('fill', 'white')
    .style('text-anchor', 'middle')
    .text(parseInt(100 * matrix['peer']) + '%');

  g.append('rect')
    .attr('x', size / 2)
    .attr('y', 0)
    .attr('width', size / 2)
    .attr('height', size / 2)
    .attr('fill', colour['tricky'])
    .style('opacity', 0.5 + 0.5 * matrix['tricky']);

  g.append('text')
    .attr('x', (3 * size) / 4)
    .attr('y', size / 4)
    .attr('dy', 4)
    .style('font-size', '8pt')
    .style('fill', 'white')
    .style('text-anchor', 'middle')
    .text(parseInt(100 * matrix['tricky']) + '%');

  let firstFreqSvg = bundle.select('#first-frequency-' + id);
  let secondFreqSvg = bundle.select('#second-frequency-' + id);
  let margin = {left: 30, right: 30};

  let sum = 0;
  for (let entry in freq['first_choice']) {
    if ({}.hasOwnProperty.call(freq['first_choice'], entry)) {
      sum += freq['first_choice'][entry];
    }
  }
  for (let entry in freq['first_choice']) {
    if ({}.hasOwnProperty.call(freq['first_choice'], entry)) {
      freq['first_choice'][entry] /= sum;
      freq['second_choice'][entry] /= sum;
    }
  }

  size = secondFreqSvg.attr('width') - margin.left;

  let x = bundle
    .scaleLinear()
    .domain([0, 1])
    .rangeRound([0, size]);
  let y = bundle
    .scaleBand()
    .domain(bundle.keys(freq['first_choice']).sort())
    .rangeRound([0, firstFreqSvg.attr('height')]);

  let gg = secondFreqSvg
    .append('g')
    .attr('transform', 'translate(' + margin.left + ',0)');

  let ggg = firstFreqSvg.append('g');

  gg.append('g')
    .attr('class', 'axis axis--x')
    .style('opacity', 0)
    .call(bundle.axisBottom(x));

  ggg
    .append('g')
    .attr('class', 'axis axis--x')
    .style('opacity', 0)
    .call(bundle.axisBottom(x));

  gg.append('g')
    .attr('class', 'axis axis--y')
    .style('opacity', 0)
    .call(bundle.axisLeft(y).ticks);

  gg.append('g')
    .selectAll('rect')
    .data(bundle.entries(freq['second_choice']))
    .enter()
    .append('rect')
    .attr('id', 'second_choice-' + id)
    .attr('finalwidth', function(d) {
      return x(d.value);
    })
    .attr('x', x(0))
    .attr('y', function(d) {
      return y(d.key);
    })
    .attr('width', 0)
    .attr(
      'height',
      firstFreqSvg.attr('height') / bundle.values(freq['second_choice']).length,
    )
    .attr('fill', 'gray')
    .style('stroke', 'white')
    .style('opacity', 0.2);

  ggg
    .append('g')
    .selectAll('rect')
    .data(bundle.entries(freq['first_choice']))
    .enter()
    .append('rect')
    .attr('id', 'first_choice-' + id)
    .attr('finalwidth', function(d) {
      return x(d.value);
    })
    .attr('finalx', function(d) {
      return x(1 - d.value);
    })
    .attr('x', x(1))
    .attr('y', function(d) {
      return y(d.key);
    })
    .attr('width', 0)
    .attr(
      'height',
      firstFreqSvg.attr('height') / bundle.values(freq['first_choice']).length,
    )
    .attr('fill', 'gray')
    .style('stroke', 'white')
    .style('opacity', 0.2);

  gg.append('g')
    .selectAll('text')
    .data(bundle.entries(freq['second_choice']))
    .enter()
    .append('text')
    .attr('x', x(0))
    .attr('dx', -2)
    .attr('y', function(d) {
      return y(d.key);
    })
    .attr('dy', y.bandwidth() / 2 + 4)
    .style('font-size', '8pt')
    .style('text-anchor', 'end')
    .text(function(d) {
      return parseInt(100 * d.value) + '%';
    });

  ggg
    .append('g')
    .selectAll('text')
    .data(bundle.entries(freq['first_choice']))
    .enter()
    .append('text')
    .attr('x', x(1))
    .attr('dx', 2)
    .attr('y', function(d) {
      return y(d.key);
    })
    .attr('dy', y.bandwidth() / 2 + 4)
    .style('font-size', '8pt')
    .style('text-anchor', 'start')
    .text(function(d) {
      return parseInt(100 * d.value) + '%';
    });

  gg.append('g')
    .selectAll('text')
    .data(bundle.entries(freq['second_choice']))
    .enter()
    .append('text')
    .attr('x', x(0))
    .attr('dx', 2)
    .attr('y', function(d) {
      return y(d.key);
    })
    .attr('dy', y.bandwidth() / 2 + 4)
    .style('font-size', '8pt')
    .text(function(d) {
      return d.key;
    });

  return;
}

/** Search function
 *  @param {String} className
 *  @param {Object} searchBar
 *  @function
 */
export function search(className, searchBar) {
  let items = document.querySelectorAll(className);
  for (let i = 0; i < items.length; i++) {
    if (
      items[i].innerText.toLowerCase().indexOf(searchBar.value.toLowerCase()) <
      0
    ) {
      items[i].style.display = 'none';
    } else {
      items[i].style.display = 'block';
    }
  }
  return;
}

/** Add dialog box to ids containing string dialog using #activate-id
 *  @function
 */
export function addDialog() {
  [].forEach.call(document.querySelectorAll('[id^=dialog]'), el => {
    const dialog = bundle.dialog.MDCDialog.attachTo(el);
    document.querySelector('#activate-' + el.id).onclick = () => {
      dialog.show();
    };
  });
}

/** Handle question delete/undelete for teacher account view
 *  @function
 *  @param {String} url
 */
export function handleQuestionDelete(url) {
  // Toggle questions
  $('.toggle-deleted-questions').click(() => {
    $('.deleted').slideToggle();
    $('#hide-deleted-questions').toggle();
    $('#show-deleted-questions').toggle();
    deletedQuestionsHidden = !deletedQuestionsHidden;
  });

  // Delete/undelete
  $('[class*=delete-question]').click(event => {
    let el = event.target;
    let pk = $(el).attr('question');
    let posting = $.post(url, {pk: pk});
    posting.done(data => {
      if (data['action'] == 'restore') {
        $('.list-item-question-' + pk).removeClass('deleted');
      } else {
        $('.list-item-question-' + pk).addClass('deleted');
      }
      $('.undelete-question-' + pk).toggle();
      $('.delete-question-' + pk).toggle();
      if (deletedQuestionsHidden == true) {
        $('.list-item-question-' + pk).slideToggle('deleted');
      }
    });
  });
}

/** Toggle image visibility
 *  @function
 */
export function toggleImages() {
  [].forEach.call(document.querySelectorAll('.toggle-images'), el => {
    const toggle = bundle.iconToggle.MDCIconToggle.attachTo(el);
    if (sessionStorage.images !== undefined) {
      if (sessionStorage.images == 'block') {
        toggle.on = true;
      } else {
        toggle.on = false;
      }
      [].forEach.call(document.querySelectorAll('.question-image'), el => {
        if (sessionStorage.images == 'block') {
          el.style.display = 'block';
        } else {
          el.style.display = 'none';
        }
      });
    }
    el.addEventListener('MDCIconToggle:change', ({detail}) => {
      [].forEach.call(document.querySelectorAll('.question-image'), el => {
        if (detail.isOn) {
          el.style.display = 'block';
        } else {
          el.style.display = 'none';
        }
        sessionStorage.images = el.style.display;
      });
    });
  });
}

/** Toggle answer visibility
 *  @function
 */
export function toggleAnswers() {
  [].forEach.call(document.querySelectorAll('.toggle-answers'), el => {
    const toggle = bundle.iconToggle.MDCIconToggle.attachTo(el);
    if (sessionStorage.answers) {
      if (sessionStorage.answers == 'block') {
        toggle.on = true;
      } else {
        toggle.on = false;
      }
      [].forEach.call(document.querySelectorAll('.question-answers'), el => {
        el.style.display = sessionStorage.answers;
      });
    }
    el.addEventListener('MDCIconToggle:change', ({detail}) => {
      [].forEach.call(document.querySelectorAll('.question-answers'), el => {
        if (detail.isOn) {
          el.style.display = 'block';
        } else {
          el.style.display = 'none';
        }
        sessionStorage.answers = el.style.display;
      });
    });
  });
}

/** Bind mdc-checkbox
 *  @function
 */
export function bindCheckbox() {
  [].forEach.call(document.querySelectorAll('.mdc-checkbox'), el => {
    bundle.checkbox.MDCCheckbox.attachTo(el);
  });
}


/** Plot student activity
 *  @function
 *  @param {String} el
  *  @param {String} d
 */
export function plotTimeSeries(el, d) {
  let svg = d3.select(el);

  let width = 0.8*$('main').innerWidth();
  svg.attr('width', width);
  let height = +svg.attr('height');

  svg.selectAll('g').remove();

  let x = d3.scaleTime()
  .domain(
    [new Date(d3.timeParse(d.distribution_date)),
      new Date(d3.timeParse(d.due_date))])
  .range([0, width]);
  let y = d3.scaleLinear().domain([0, d.total]).range([height, 0]);

  let xAxis = d3.axisBottom(x);
  let xAxisTop = d3.axisTop(x).ticks('');

  let g = svg.append('g');

  g.append('rect')
  .attr('fill', 'white')
  .attr('x', 0)
  .attr('y', 0)
  .attr('width', width)
  .attr('height', height);

  g.append('g').attr('transform', 'translate(0,'+height+')').call(xAxis);
  g.append('g').call(xAxisTop);

  let format = d3.timeFormat("%c");

  let f = d3.line()
  .x(function(d) {
    return x(new Date(d3.timeParse(d)));
  })
  .y(function(d, i) {
    return y(i+1);
  })
  .curve(d3.curveStepAfter);

  g.append('g')
  .selectAll('path')
  .data([d.answers])
  .enter().append('path')
  .attr('stroke', '#004266')
  .attr('stroke-width', '2px')
  .attr('stroke-linecap', 'round')
  .attr('fill', 'none')
  .attr('d', f);

  if (d.due_date > d.last_login) {
    let endDate = Math.min(
      new Date(d3.timeParse(d.now)),
      new Date(d3.timeParse(d.due_date)),
    );
    g.append('rect')
    .attr('stroke', 'black')
    .attr('stroke-width', '1px')
    .attr('fill', 'gray')
    .style('opacity', 0.2)
    .attr('x', function() {
      return x(new Date(d3.timeParse(d.last_login)));
    })
    .attr('y', function() {
      return 0;
    })
    .attr('width', function() {
      return x(endDate)
        - x(new Date(d3.timeParse(d.last_login)));
    })
    .attr('height', height);
  }

  g.append('path')
  .attr('class', 'slider')
  .attr('stroke', 'gray')
  .attr('stroke-width', '0.5px')
  .attr('d', function() {
    let path = d3.path();
    path.moveTo(0, height+30);
    path.lineTo(0, -6);
    return path;
  });

  g.append('text')
  .attr('x', width)
  .attr('dx', -5)
  .attr('y', -25)
  .attr('text-anchor', 'end')
  .style('font-size', '10px')
  .style('font-family', 'sans-serif')
  .text(format(new Date(d3.timeParse(d.due_date))));

  g.append('text')
  .attr('x', 0)
  .attr('dx', 5)
  .attr('y', -25)
  .attr('text-anchor', 'start')
  .style('font-size', '10px')
  .style('font-family', 'sans-serif')
  .text(format(new Date(d3.timeParse(d.distribution_date))));

  g.append('path')
  .attr('class', 'limit')
  .attr('stroke', 'gray')
  .attr('stroke-dasharray', 4)
  .attr('stroke-width', '0.5px')
  .attr('d', function() {
    let path = d3.path();
    path.moveTo(0, height);
    path.lineTo(0, -30);
    return path;
  });

  g.append('path')
  .attr('class', 'limit')
  .attr('stroke', 'gray')
  .attr('stroke-dasharray', 4)
  .attr('stroke-width', '0.5px')
  .attr('d', function() {
    let path = d3.path();
    path.moveTo(width, height);
    path.lineTo(width, -30);
    return path;
  });

  g.append('text')
  .attr('class', 'slider-label-bottom')
  .attr('x', 0)
  .attr('dx', 5)
  .attr('y', height+25)
  .attr('dy', 5)
  .attr('text-anchor', 'start')
  .style('font-size', '10px')
  .style('font-family', 'sans-serif')
  .text();

  g.append('text')
  .attr('class', 'slider-label-top')
  .attr('x', 0)
  .attr('y', -6)
  .attr('dy', -5)
  .attr('text-anchor', 'middle')
  .style('font-size', '10px')
  .style('font-family', 'sans-serif')
  .text();

  let area = d3.area()
  .x0(f.x())
  .y0(height)
  .x1(f.x())
  .y1(f.y())
  .curve(d3.curveStepAfter);

  svg.on('mousemove', /* @this */ function() {
      let xValue = Math.min(
        d3.mouse(this)[0],
        1+x(d3.max(d.answers.map(x => new Date(d3.timeParse(x)))))
      );

      g.select('.slider').attr('d', function() {
        let path = d3.path();
        path.moveTo(xValue, height+30);
        path.lineTo(xValue, -6);
        return path;
      });

      g.select('.slider-label-bottom').attr('text-anchor', function() {
        if (xValue < width/2) {
          return 'start';
        } else {
          return 'end';
        }
      })
      .attr('dx', function() {
        if (xValue < width/2) {
          return 5;
        } else {
          return -5;
        }
      })
      .attr('x', xValue)
      .text(format(x.invert(xValue)));

      g.select('.slider-label-top')
      .attr('x', xValue)
      .text(parseInt(
        100*d3.bisectLeft(
          d.answers.map(x => new Date(d3.timeParse(x))), x.invert(xValue))
          /d.total)+"%");

      let data = d.answers.map(x => new Date(d3.timeParse(x)));
      let index = d3.bisectLeft(data, x.invert(xValue));

      data = data.slice(0, index);

      if (data.length < d.answers.length) {
        data.push(x.invert(xValue));
      }

      g.select(".area").remove();
      g.append("path")
      .datum(data)
      .attr("class", "area")
      .attr("d", area);
  });
}

// Commands
underlines();

// Listeners
window.addEventListener('resize', underlines);

// MDC
autoInit();
