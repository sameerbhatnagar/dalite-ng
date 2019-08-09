// @flow
"use strict";
import { buildReq } from "../../../../../peerinst/static/peerinst/js/ajax.js";
import {
  clear,
  createSvg,
  svgLink,
} from "../../../../../peerinst/static/peerinst/js/utils.js";
import * as d3 from "d3";
import { ReputationHeader } from "./header.js";

class StudentReputationHeader extends ReputationHeader {
  async init(shadow: ShadowRoot) {
    /*********/
    /* model */
    /*********/

    type Reputation = {
      name: string,
      description: string,
      reputation: number,
      badgeThresholds: Array<number>,
      badgeColour: string,
    };

    type Model = {
      id: number,
      element: StudentReputationHeader,
      reputationType: string,
      reputationUrl: string,
      reputations: Array<Reputation>,
      shadow: ShadowRoot,
    };

    const model: Model = {
      id: parseInt(this.reputationId),
      element: this,
      reputationType: "student",
      reputationUrl: this.reputationUrl,
      reputations: [],
      shadow: shadow,
    };

    /**********/
    /* update */
    /**********/

    async function update() {
      await getReputation();
      if (model.reputations.length) {
        model.element.hidden = false;
      }
    }

    async function getReputation() {
      const postData = {
        reputation_type: model.reputationType,
        id: model.id,
      };
      const req = buildReq(postData, "post");
      const resp = await fetch(model.reputationUrl, req);
      const data = await resp.json();
      model.reputations = data.reputations.map(reputation => ({
        name: reputation.full_name,
        description: reputation.description,
        reputation: reputation.reputation,
        badgeThresholds: reputation.badge_thresholds,
        badgeColour: reputation.badge_colour,
      }));
      iconView();
      listView();
    }

    function toggleReputationList() {
      model.element.open = !model.element.open;
      iconView();
      listView();
      toggleReputationView();
    }

    /********/
    /* view */
    /********/

    function view() {
      model.shadow.appendChild(styleView());

      const container = document.createElement("div");
      container.id = "container";
      model.shadow.appendChild(container);

      container.appendChild(iconView());
      container.appendChild(listView());
    }

    function iconView() {
      let icon = model.shadow.querySelector("#icon");

      if (!icon) {
        icon = document.createElement("div");
        icon.id = "icon";
        icon.title = "Reputation";
        icon.addEventListener("click", (event: MouseEvent) => {
          event.stopPropagation();
          toggleReputationList();
        });

        const symbol = createSvg("donut_small", false);
        symbol.id = "icon__icon";
        icon.appendChild(symbol);

        // $FlowFixMe
        document.body?.addEventListener("click", (event: MouseEvent) => {
          if (model.element.open) {
            toggleReputationList();
          }
        });
      }

      return icon;
    }

    function listView() {
      let list = model.shadow.querySelector("#list");
      if (!list) {
        list = document.createElement("div");
        list.id = "list";
        list.addEventListener("click", (event: MouseEvent) => {
          event.stopPropagation();
        });
      }

      clear(list);

      model.reputations.forEach(reputation => {
        reputationView(list, reputation);
      });

      return list;
    }

    function reputationView(list: HTMLElement, reputation: Reputation) {
      const name = document.createElement("div");
      name.classList.add("list__name");
      name.textContent = `${reputation.name}`;
      name.title = reputation.description;
      list.appendChild(name);

      list.appendChild(
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
      container.classList.add("badge");

      const scale = 2;
      const height = 8;

      const svg = d3
        .select(container)
        .append("svg")
        .attr("viewBox", `0 0 ${100 * scale} ${20 * scale}`)
        .append("g");

      svg
        .append("text")
        .attr("data-val", reputation)
        .attr("dominant-baseline", "central")
        .attr("x", 5 * scale)
        .attr("y", 10 * scale)
        .attr("class", "fill-primary badge__reputation")
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
        .attr("stroke", "var(--reputation-colour)")
        .attr("stroke-width", 1)
        .attr("fill", "none");

      svg
        .append("rect")
        .attr("class", "badge__bar")
        .attr("x", 20 * scale)
        .attr("y", ((20 - height) / 2) * scale)
        .attr("height", height * scale)
        .attr("width", Math.min((75 * reputation) / 100, height / 2) * scale)
        .attr("rx", (height / 2) * scale)
        .attr("ry", (height / 2) * scale)
        .attr("stroke", "var(--reputation-colour)")
        .attr("stroke-width", 1)
        .attr("fill", "var(--reputation-colour)");

      badgeThresholds.forEach(threshold => {
        const badge = svg
          .append("g")
          .attr("height", height * scale)
          .attr("width", height * scale)
          .attr("fill", badgeColour)
          .attr("fill-opacity", reputation < threshold ? 0.5 : 1);
        badge.append("use").attr("xlink:href", svgLink("donut_small", false));

        if (reputation < threshold) {
          badge.append("title").text(`Next badge at ${threshold}`);
        } else {
          badge.append("title").text(`Obtained at ${threshold}`);
        }
      });

      // const badgeArc = d3
      // .arc()
      // .innerRadius(((height * 5) / 32) * scale)
      // .outerRadius((height / 2) * scale)
      // .padAngle(0.9)
      // .padRadius((height / 8) * scale);
      // const badgeArcs = d3.pie()([2, 1, 1]);
      //
      // badgeThresholds.forEach(threshold => {
      // const badge = svg
      // .append("g")
      // .attr(
      // "transform",
      // "translate(" +
      // `${(20 + (threshold * 75) / 100 - height / 2) * scale}, ` +
      // `${10 * scale}` +
      // ")" +
      // " rotate(180)",
      // );
      //
      // if (reputation < threshold) {
      // badge.append("title").text(`Next badge at ${threshold}`);
      // } else {
      // badge.append("title").text(`Obtained at ${threshold}`);
      // }
      //
      // badge
      // .append("circle")
      // .attr("cx", 0)
      // .attr("cy", 0)
      // .attr("r", (height / 2) * scale)
      // .attr("fill", "#ffffff");
      //
      // badge
      // .selectAll("arc")
      // .data(badgeArcs)
      // .enter()
      // .append("g")
      // .attr("class", "arc")
      // .append("path")
      // .attr("d", badgeArc)
      // .attr("fill", badgeColour)
      // .attr("fill-opacity", reputation < threshold ? 0.5 : 1);
      // });

      return container;
    }

    function toggleReputationView() {
      const duration = 500;
      const scale = 2;
      const height = 8;

      const counts = model.shadow.querySelectorAll(".badge__reputation");
      const bars = model.shadow.querySelectorAll(".badge__bar");

      for (let i = 0; i < model.reputations.length; i++) {
        const reputation = model.reputations[i].reputation;
        const count = d3.select(counts[i]);
        const bar = d3.select(bars[i]);
        if (model.element.open) {
          count
            .transition()
            .duration(duration)
            .ease(d3.easeCubicInOut)
            .tween("text", function() {
              const interpolate = d3.interpolate(
                this.textContent, // eslint-disable-line
                reputation,
              );
              return function(t) {
                this.textContent = Math.round(interpolate(t)); // eslint-disable-line
              };
            });
          bar
            .transition()
            .duration(duration)
            .ease(d3.easeCubicInOut)
            .attr("width", (75 * scale * reputation) / 100);
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
            .attr(
              "width",
              Math.min((75 * reputation) / 100, height / 2) * scale,
            );
        }
      }
    }

    function styleView() {
      const style = document.createElement("link");
      style.setAttribute(
        "href",
        window.location.protocol +
          "//" +
          window.location.host +
          "/static/reputation/css/header/student.min.css",
      );
      style.setAttribute("rel", "stylesheet");
      style.setAttribute("nonce", model.element.nonce_);
      return style;
    }

    /********/
    /* init */
    /********/

    view();
    await update();
  }
}

if (!customElements.get("student-reputation-header")) {
  customElements.define("student-reputation-header", StudentReputationHeader);
}
