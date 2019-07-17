// @flow

import { clear, createSvg } from "../utils.js";

/*********/
/* model */
/*********/

type Notification = {
  text: string,
  inProgress: boolean,
  onClick: () => void,
};

let model: {
  notificationsOpen: boolean,
  notifications: Array<Notification>,
};

function initModel(notifications: Array<Notification>): void {
  model = {
    notificationsOpen: false,
    notifications: notifications,
  };
}

/**********/
/* update */
/**********/

function toggleNotifications(): void {
  model.notificationsOpen = !model.notificationsOpen;
  notificationsView();
}

/********/
/* view */
/********/

function view(): void {
  notificationsView();
}

function notificationsView(): void {
  const notifications = document.querySelector(".notifications");
  const badge = notifications?.querySelector(".notifications__icon__badge");
  const notificationsList = notifications?.querySelector(
    ".notifications__notifications",
  );

  if (!notifications || !badge || !notificationsList) {
    return;
  }

  if (model.notifications.length) {
    badge.textContent = model.notifications.length.toString();
    badge.style.display = "flex";
  } else {
    badge.textContent = "";
    badge.style.display = "none";
  }

  clear(notificationsList);
  if (model.notifications.length) {
    model.notifications.map(function(notification) {
      notificationsList.appendChild(notificationView(notification));
    });
  } else {
    notificationsList.appendChild(noNotificationView());
  }

  if (model.notificationsOpen) {
    notifications.classList.add("notifications--open");
  } else {
    notifications.classList.remove("notifications--open");
  }
}

function notificationView(notification: Notification): HTMLDivElement {
  const div = document.createElement("div");
  div.classList.add("notification");
  div.addEventListener("click", notification.onClick);

  if (notification.inProgress) {
    const spinner = document.createElement("loading-spinner");
    spinner.classList.add("notification__spinner");
    div.appendChild(spinner);
  } else {
    const icon = createSvg("cloud_download");
    icon.classList.add("notification__icon");
    div.appendChild(icon);
  }

  const description = document.createElement("span");
  description.classList.add("notification__description");
  description.textContent = notification.text;
  div.appendChild(description);

  return div;
}

function noNotificationView(): HTMLDivElement {
  const div = document.createElement("div");
  div.textContent = "No new notifications";
  return div;
}

/*************/
/* listeners */
/*************/

function initEventListeners(): void {
  addNotificationsOpenListener();
}

function addNotificationsOpenListener(): void {
  document
    .querySelector(".notifications")
    ?.addEventListener("click", function(event: MouseEvent) {
      event.stopPropagation();
    });
  document
    .querySelector(".notifications__icon")
    ?.addEventListener("click", function(event: MouseEvent) {
      toggleNotifications();
    });
  document.body?.addEventListener("click", function(event: MouseEvent) {
    if (model.notificationsOpen) {
      toggleNotifications();
    }
  });
}

/********/
/* init */
/********/

export function init(notifications: Array<Notification>): void {
  initModel(notifications);
  view();
  initEventListeners();
}
