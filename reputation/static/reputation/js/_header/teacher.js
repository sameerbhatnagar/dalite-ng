// @flow
import { buildReq } from "../../../../../peerinst/static/peerinst/js/ajax.js";
import {
  clear,
  createSvg,
} from "../../../../../peerinst/static/peerinst/js/utils.js";

export class TeacherReputationHeader extends HTMLElement {
  get reputationUrl(): string {
    const url = this.getAttribute("reputation-url");
    if (!url) {
      throw new Error(
        "The teacher-reputation-header needs a `reputation-url` attribute",
      );
    }
    return url;
  }
  get reputationType(): string {
    const type = this.getAttribute("reputation-type");
    if (!type) {
      throw new Error(
        "The teacher-reputation-header needs a `reputation-type` attribute",
      );
    }
    return type;
  }
  get reputationId(): string {
    const id = this.getAttribute("reputation-id");
    if (!id) {
      throw new Error(
        "The teacher-reputation-header needs a `reputation-id` attribute",
      );
    }
    return id;
  }
  get nonce(): string {
    const nonce = this.getAttribute("nonce");
    if (!nonce) {
      throw new Error(
        "The teacher-reputation-header needs a `nonce` attribute",
      );
    }
    return nonce;
  }
  get hidden() {
    return this.hasAttribute("hidden");
  }
  get open() {
    return this.hasAttribute("hidden");
  }
  set hidden(val: boolean) {
    if (val) {
      this.setAttribute("hidden", "");
    } else {
      this.removeAttribute("hidden");
    }
  }
  set open(val: boolean) {
    if (val) {
      this.setAttribute("hidden", "");
    } else {
      this.removeAttribute("hidden");
    }
  }

  constructor() {
    super();

    const shadow = this.attachShadow({ mode: "open" });

    this.init(shadow);
  }

  async init(shadow: ShadowRoot) {
    /*********/
    /* model */
    /*********/

    const model = {
      id: parseInt(this.reputationId),
      nonce: this.nonce,
      open: this.open,
      reputation: null,
      reputationType: this.reputationType,
      reputationUrl: this.reputationUrl,
      reputations: [],
      shadow: shadow,
    };

    /**********/
    /* update */
    /**********/

    async function update() {
      // await getReputation();
    }

    async function getReputation() {
      const postData = {
        reputation_type: model.reputationType,
        id: model.id,
      };
      const req = buildReq(postData, "post");
      const resp = await fetch(model.reputationUrl, req);
      const data = await resp.json();
      model.reputation = data.reputation;
      model.reputations = data.reputations;
    }

    function toggleReputationList() {
      model.open = !model.open;
      listView();
    }

    /********/
    /* view */
    /********/

    function view() {
      const container = document.createElement("div");
      container.id = "container";
      container.title = "Reputation";
      shadow.appendChild(container);

      container.appendChild(iconView());
      container.appendChild(listView());
      container.appendChild(styleView());
    }

    function iconView() {
      const icon = document.createElement("div");
      icon.id = "icon";
      icon.addEventListener("click", (event: MouseEvent) => {
        event.stopPropagation();
      });

      const star = createSvg("star");
      star.id = "icon__icon";
      star.addEventListener("click", (event: MouseEvent) => {
        toggleReputationList();
      });
      icon.appendChild(star);

      const span = document.createElement("span");
      span.id = "icon__reputation";
      icon.appendChild(span);

      document.body?.addEventListener("click", (event: MouseEvent) => {
        if (model.open) {
          toggleReputationList();
        }
      });

      return icon;
    }

    function listView() {
      let list = document.getElementById("list");
      if (!list) {
        list = document.createElement("div");
        list.id = "list";
      }

      clear(list);

      headerView(list);

      model.reputations.forEach(reputation => {
        reputationView(list, reputation);
      });

      return list;
    }

    function headerView(list) {
      const name = document.createElement("div");
      name.classList.add("list__header");
      name.textContent = "Name";
      list.appendChild(name);

      const rep = document.createElement("div");
      rep.classList.add("list__header");
      rep.textContent = "Reputation";
      list.appendChild(rep);
    }

    function reputationView(list, reputation) {
      const name = document.createElement("div");
      name.classList.add("list__name");
      name.textContent = `${reputation.full_name}`;
      name.title = reputation.description;
      list.appendChild(name);

      const rep = document.createElement("div");
      rep.textContent = Math.round(reputation.reputation * 100) / 100;
      list.appendChild(rep);
    }

    function styleView() {
      const style = document.createElement("style");
      style.textContent = `
        #container {
          position: relative;
        }

        #icon {
          align-items: center;
          border-radius: 20px;
          cursor: pointer;
          display: flex;
          justify-content: space-between;
          padding: 4px;
          transition: 200ms;
        }

        #icon:hover {
          background: rgba(255, 255, 255, 0.25);
        }

        #icon:active {
          background: rgba(255, 255, 255, 0.5);
        }

        #icon__icon {
          fill: var(--reputation-icon-colour, #ffffff);
          height: 30px;
          width: 30px;
        }

        #reputation {
          text-align: center;
          width: 45px;
        }

        #list {
          align-items: center;
          background: #ffffff;
          border-radius: 20px;
          color: var(--reputation-text-colour, #000000);
          display: grid;
          font-size: 0.9rem;
          grid-auto-rows: minmax(50px, max-content);
          grid-template-columns: repeat(3, minmax(125px, max-content));
          padding: 10px;
          position: absolute;
          right: 0;
          text-align: center;
          top: 40px;
          transform: scale(0);
          transform-origin: top right;
          transition: transform 200ms, border-radius 200ms;
          z-index: 10;
        }

        .list__header {
          align-content: center;
          color: var(--reputation-header-colour, #000000)
          font-size: 1.1rem;
          font-weight: bold;
          justify-content: center;
          text-decoration: underline;
          user-select: none;
        }

        .list__name {
          cursor: pointer;
          text-decoration: underline;
        }

        :host([hidden]) {
            display: none;
        }

        :host([open]) #icon {
          background: #ffffff;
          border-radius: 20px 20px 0 0;
          color: var(--reputation-colour, #d3d3d3);
          fill: var(--reputation-colour, #d3d3d3);
        }

        :host([open]) #list {
          border-radius: 20px 0 20px 20px;
          transform: scale(1);
        }
      `;
      style.setAttribute("nonce", model.nonce);
      return style;
    }

    /********/
    /* init */
    /********/

    await update();
    view();
  }
}
