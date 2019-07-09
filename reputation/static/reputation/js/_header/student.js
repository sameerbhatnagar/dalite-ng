// @flow
import { buildReq } from "../../../../../peerinst/static/peerinst/js/_ajax/utils.js"; // eslint-disable-line
import { clear } from "../../../../../peerinst/static/peerinst/js/utils.js"; // eslint-disable-line
import * as d3 from "d3";

/*********/
/* model */
/*********/

let model: {
  mdcThemePrimary: string,
  reputationListOpen: boolean,
  reputationUrl: string,
  reputationType: string,
  id: number,
  reputations: Array<{
    name: string,
    full_name: string,
    description: string,
    reputation: number,
    badgeThresholds: Array<number>,
    badgeColour: string,
  }>,
};

function initModel(reputationUrl, reputationType, id) {
  model = {
    mdcThemePrimary: "#54c0db",
    reputationListOpen: false,
    reputationUrl: reputationUrl,
    reputationType: reputationType,
    id: id,
    reputations: [],
  };
}

/**********/
/* update */
/**********/

async function update() {
  await getReputation();
}

async function getReputation() {
  const postData = {
    reputation_type: model.reputationType,
    id: model.id,
  };
  const req = buildReq(postData, "post");
  const resp = await fetch(model.reputationUrl, req);
  const data = await resp.json();
  model.reputations = data.reputations.map(r => ({
    name: r.name,
    full_name: r.full_name,
    description: r.description,
    reputation: r.reputation,
    badgeThresholds: r.badge_thresholds,
    badgeColour: r.badge_colour,
  }));
}

function toggleReputationList() {
  model.reputationListOpen = !model.reputationListOpen;
  // reputationListView();
  toggleReputationView();
}

/********/
/* view */
/********/

function view() {
  iconView();
  reputationListView();
}

function iconView() {
  document
    .querySelector(".reputation-icon")
    ?.classList.remove("reputation-icon--hidden");
}

function reputationListView() {
  const container = document.querySelector(".reputation-icon__list");
  if (!container) {
    throw new Error(
      "The element with class .reputation-icon__list is missing",
    );
  }
  clear(container);
  model.reputations.forEach(reputation => {
    reputationView(container, reputation);
  });
  toggleReputationView();
}

function reputationView(
  container: HTMLElement,
  reputation: {
    name: string,
    full_name: string,
    description: string,
    reputation: number,
    badgeThresholds: Array<number>,
    badgeColour: string,
  },
) {
  const name = document.createElement("div");
  name.classList.add("reputation-icon__list__name");
  name.textContent = `${reputation.full_name}`;
  name.title = reputation.description;
  container.appendChild(name);

  container.appendChild(
    progressView(
      reputation.name,
      reputation.reputation,
      reputation.badgeThresholds,
      reputation.badgeColour,
    ),
  );
}

function progressView(
  name: string,
  reputation: number,
  badgeThresholds: Array<number>,
  badgeColour: string,
): HTMLElement {
  const container = document.createElement("div");
  container.classList.add("student-badge");

  const scale = 2;
  const height = 8;

  const svg = d3
    .select(container)
    .append("svg")
    .attr("viewBox", `0 0 ${100 * scale} ${20 * scale}`)
    .append("g");

  svg
    .append("text")
    .attr("data-val", Math.round(reputation * 100))
    .attr("dominant-baseline", "central")
    .attr("x", 5 * scale)
    .attr("y", 10 * scale)
    .attr("class", "fill-primary student-badge__reputation")
    .attr("font-size", 8 * scale)
    .text(0);

  svg
    .append("rect")
    .attr("x", 20 * scale)
    .attr("y", ((20 - height) / 2) * scale)
    .attr("height", height * scale)
    .attr("width", 75 * scale)
    .attr("rx", (height / 2) * scale)
    .attr("ry", (height / 2) * scale)
    .attr("stroke", model.mdcThemePrimary)
    .attr("stroke-width", 1)
    .attr("fill", "none");

  svg
    .append("rect")
    .attr("class", "student-badge__bar")
    .attr("x", 20 * scale)
    .attr("y", ((20 - height) / 2) * scale)
    .attr("height", height * scale)
    .attr("width", Math.min(75 * reputation, height / 2) * scale)
    .attr("rx", (height / 2) * scale)
    .attr("ry", (height / 2) * scale)
    .attr("stroke", model.mdcThemePrimary)
    .attr("stroke-width", 1)
    .attr("fill", model.mdcThemePrimary);

  const badgeArc = d3
    .arc()
    .innerRadius(((height * 5) / 32) * scale)
    .outerRadius((height / 2) * scale)
    .padAngle(0.9)
    .padRadius((height / 8) * scale);
  const badgeArcs = d3.pie()([2, 1, 1]);

  badgeThresholds.forEach(threshold => {
    const badge = svg
      .append("g")
      .attr(
        "transform",
        "translate(" +
          `${(20 + threshold * 75 - height / 2) * scale}, ` +
          `${10 * scale}` +
          ")" +
          " rotate(180)",
      );

    if (reputation < threshold) {
      badge.append("title").text(`Next badge at ${threshold * 100}`);
    } else {
      badge.append("title").text(`Obtained at ${threshold * 100}`);
    }

    badge
      .append("circle")
      .attr("cx", 0)
      .attr("cy", 0)
      .attr("r", (height / 2) * scale)
      .attr("fill", "#ffffff");

    badge
      .selectAll("arc")
      .data(badgeArcs)
      .enter()
      .append("g")
      .attr("class", "arc")
      .append("path")
      .attr("d", badgeArc)
      .attr("fill", badgeColour)
      .attr("fill-opacity", reputation < threshold ? 0.5 : 1);
  });

  return container;
}

function toggleReputationView() {
  const duration = 500;
  const scale = 2;
  const height = 8;

  if (model.reputationListOpen) {
    document
      .querySelector(".reputation-icon")
      ?.classList.add("reputation-icon--open");
  } else {
    document
      .querySelector(".reputation-icon")
      ?.classList.remove("reputation-icon--open");
  }

  const counts = document.getElementsByClassName("student-badge__reputation");
  const bars = document.getElementsByClassName("student-badge__bar");

  for (let i = 0; i < model.reputations.length; i++) {
    const reputation = model.reputations[i].reputation;
    const count = d3.select(counts[i]);
    const bar = d3.select(bars[i]);
    if (model.reputationListOpen) {
      count
        .transition()
        .duration(duration)
        .ease(d3.easeCubicInOut)
        .tween("text", function() {
          const interpolate = d3.interpolate(
            this.textContent, // eslint-disable-line
            Math.round(reputation * 100),
          );
          return function(t) {
            this.textContent = Math.round(interpolate(t)); // eslint-disable-line
          };
        });
      bar
        .transition()
        .duration(duration)
        .ease(d3.easeCubicInOut)
        .attr("width", 75 * scale * reputation);
    } else {
      count
        .transition()
        .duration(duration)
        .ease(d3.easeCubicInOut)
        .tween("text", function() {
          const interpolate = d3.interpolate(this.textContent, 0); // eslint-disable-line
          return function(t) {
            this.textContent = Math.round(interpolate(t)); // eslint-disable-line
          };
        });
      bar
        .transition()
        .duration(duration)
        .ease(d3.easeCubicInOut)
        .attr("width", Math.min(75 * reputation, height / 2) * scale);
    }
  }
}

/*************/
/* listeners */
/*************/

function addEventListeners() {
  addReputationListOpenListener();
}

function addReputationListOpenListener() {
  document
    .querySelector(".reputation-icon")
    ?.addEventListener("click", function(event: MouseEvent) {
      event.stopPropagation();
    });
  document
    .querySelector(".reputation-icon__icon")
    ?.addEventListener("click", function(event: MouseEvent) {
      toggleReputationList();
    });
  document.body?.addEventListener("click", function(event: MouseEvent) {
    if (model.reputationListOpen) {
      toggleReputationList();
    }
  });
}

/********/
/* init */
/********/

export async function init(url: string, reputationType: string, id: number) {
  initModel(url, reputationType, id);
  await update();
  view();
  addEventListeners();
}
