// @flow
import { buildReq } from "../../../../../dalite/static/js/ajax.js";

/*********/
/* model */
/*********/

type Collection = {
  title: string,
  description: string,
  discipline: string,
  nAssignments: number,
  nFollowers: number,
};

let model: {
  collections: Array<Collection>,
  urls: {
    collections: string,
  },
};

function initModel(data: { urls: { collections: string } }) {
  model = {
    collections: [],
    urls: {
      collections: data.urls.collections,
    },
  };
}

/**********/
/* update */
/**********/

async function update() {
  await getCollections();
}

async function getCollections() {
  const data = {};
  const req = buildReq(data, "post");
  const resp = await fetch(model.urls.collections, req);
  const json = await resp.json();
  model.collections = json.collections.map(collection => ({
    title: collection.title,
    description: collection.description,
    discipline: collection.discipline,
    nAssignments: collection.n_assignments,
    nFollowers: collection.n_followers,
  }));
  collectionsView();
}

/********/
/* view */
/********/

function collectionsView() {
  const section = document.querySelector(".collections");
  if (!section) {
    throw new Error("There is a missing section with class `collections`");
  }
  if (model.collections.length) {
    section.classList.remove("collections--hidden");
  } else {
    section.classList.add("collections--hidden");
  }
}

/********/
/* init */
/********/

export async function init(data: { urls: { collections: string } }) {
  initModel(data);
  await update();
}
