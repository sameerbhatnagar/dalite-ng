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
  get nonce_(): string {
    const nonce = this.getAttribute("nonce") || this.nonce;
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
    return this.hasAttribute("open");
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
      this.setAttribute("open", "");
    } else {
      this.removeAttribute("open");
    }
  }

  constructor() {
    super();

    const shadow = this.attachShadow({ mode: "open" });

    this.hidden = true;

    this.init(shadow);
  }

  async init(shadow: ShadowRoot) {
    /*********/
    /* model */
    /*********/

    type Reputation = {
      name: string,
      description: string,
      reputation: number,
    };

    type Model = {
      id: number,
      element: TeacherReputationHeader,
      reputation: ?number,
      reputationType: string,
      reputationUrl: string,
      reputations: Array<Reputation>,
      shadow: ShadowRoot,
    };

    const model: Model = {
      id: parseInt(this.reputationId),
      element: this,
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
      await getReputation();
      if (model.reputation !== null) {
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
      model.reputation = data.reputation;
      model.reputations = data.reputations.map(reputation => ({
        name: reputation.full_name,
        description: reputation.description,
        reputation: reputation.reputation,
      }));
      iconView();
      listView();
    }

    function toggleReputationList() {
      model.element.open = !model.element.open;
      iconView();
      listView();
    }

    /********/
    /* view */
    /********/

    function view() {
      shadow.appendChild(styleView());

      const container = document.createElement("div");
      container.id = "container";
      shadow.appendChild(container);

      container.appendChild(iconView());
      container.appendChild(listView());
    }

    function iconView() {
      let icon = shadow.getElementById("icon");

      if (!icon) {
        icon = document.createElement("div");
        icon.id = "icon";
        icon.title = "Reputation";
        icon.addEventListener("click", (event: MouseEvent) => {
          event.stopPropagation();
          toggleReputationList();
        });

        const star = createSvg("star", false);
        star.id = "icon__icon";
        icon.appendChild(star);

        const span = document.createElement("span");
        span.id = "icon__reputation";
        if (model.reputation !== null && model.reputation !== undefined) {
          span.textContent = model.reputation.toString();
        }
        icon.appendChild(span);

        document.body?.addEventListener("click", (event: MouseEvent) => {
          if (model.element.open) {
            toggleReputationList();
          }
        });
      } else {
        if (model.reputation !== null && model.reputation !== undefined) {
          shadow.getElementById(
            "icon__reputation",
          ).textContent = model.reputation.toString();
        }
      }

      return icon;
    }

    function listView() {
      let list = shadow.getElementById("list");
      if (!list) {
        list = document.createElement("div");
        list.id = "list";
        list.addEventListener("click", (event: MouseEvent) => {
          event.stopPropagation();
        });
      }

      clear(list);

      headerView(list);

      model.reputations.forEach(reputation => {
        reputationView(list, reputation);
      });

      return list;
    }

    function headerView(list: HTMLElement) {
      const name = document.createElement("div");
      name.classList.add("list__header");
      name.textContent = "Name";
      list.appendChild(name);

      const rep = document.createElement("div");
      rep.classList.add("list__header");
      rep.textContent = "Reputation";
      list.appendChild(rep);
    }

    function reputationView(list: HTMLElement, reputation: Reputation) {
      const name = document.createElement("div");
      name.classList.add("list__name");
      name.textContent = `${reputation.name}`;
      name.title = reputation.description;
      list.appendChild(name);

      const rep = document.createElement("div");
      rep.textContent = (
        Math.round(reputation.reputation * 100) / 100
      ).toString();
      list.appendChild(rep);
    }

    function styleView() {
      const style = document.createElement("link");
      style.setAttribute(
        "href",
        window.location.protocol +
          "//" +
          window.location.host +
          "/static/reputation/css/teacher-header.min.css",
      );
      style.setAttribute("rel", "stylesheet");
      style.setAttribute("nonce", model.nonce);
      return style;
    }

    /********/
    /* init */
    /********/

    view();
    await update();
  }
}
