import { buildReq } from "../../ajax.js";
import { createSvg } from "../../utils.js";

/*********/
/* model */
/*********/

let model;

function initModel(data) {
  model = {
    urls: {
      daliteMessages: data.urls.daliteMessages,
      removeDaliteMessage: data.urls.removeDaliteMessage,
    },
    messages: [],
  };
}

/**********/
/* update */
/**********/

async function update() {
  await getMessages();
}

async function getMessages() {
  const req = buildReq({}, "post");

  const resp = await fetch(model.urls.daliteMessages, req);
  const data = await resp.json();
  model.messages = data.messages.map(message => ({
    id: message.id,
    title: message.title,
    text: message.text,
    colour: message.colour,
    removable: message.removable,
    link: message.link,
    authors: message.authors.map(author => ({
      name: author.name,
      picture: author.picture,
    })),
  }));
}

async function removeMessage(message, div) {
  const data = {
    id: message.id,
  };
  const req = buildReq(data, "post");

  const resp = await fetch(model.urls.removeDaliteMessage, req);
  if (resp.ok) {
    removeMessageView(div);
  }
}

/********/
/* view */
/********/

function view() {
  messagesView();
}

function messagesView() {
  const ul = document.querySelector("#dalite-messages ul");
  model.messages.forEach(message => {
    ul.appendChild(messageView(message));
  });
}

function messageView(message) {
  const container = document.createElement("li");
  container.classList.add("mdc-card", "dalite-message");
  if (message.link) {
    container.addEventListener("click", () => {
      window.location.assign(message.link);
    });
    container.style.setProperty("cursor", "pointer");
    container.title = message.link;
  }

  if (message.authors.length) {
    const authorsContainer = document.createElement("div");
    authorsContainer.classList.add("dalite-message__authors");
    message.authors.forEach(author => {
      const img = document.createElement("img");
      img.classList.add("dalite-message__authors__author");
      img.title = author.name;
      img.setAttribute("src", author.picture);
      img.setAttribute("alt", `Picture of ${author.name}`);
      authorsContainer.appendChild(img);
    });
    container.appendChild(authorsContainer);
  }

  const title = document.createElement("div");
  title.classList.add("mdc-typography--title", "dalite-message__title");
  title.textContent = message.title;
  container.appendChild(title);

  const text = document.createElement("div");
  text.classList.add("mdc-typography--body1", "dalite-message__text");
  text.textContent = message.text;
  container.appendChild(text);

  if (message.removable) {
    const remove = document.createElement("div");
    remove.classList.add("dalite-message__remove-icon");
    remove.addEventListener("click", async () => {
      await removeMessage(message, container);
    });
    const icon = createSvg("close");
    remove.appendChild(icon);
    container.appendChild(remove);
  }

  const background = document.createElement("div");
  background.classList.add("dalite-message__background");
  background.style.setProperty("background", message.colour);
  container.appendChild(background);

  return container;
}

function removeMessageView(node) {
  node.parentNode.removeChild(node);
}

/********/
/* init */
/********/

export async function init(data) {
  initModel(data);
  await update();
  view();
}
