// @flow
import { buildReq } from "../_ajax/utils.js";
import { init as initNotifications } from "./notifications.js";

/*********/
/* model */
/*********/

let model: {
  urls: {
    requestReport: string,
    reportResult: string,
    tasks: string,
  },
  tasks: Array<{
    id: string,
    description: string,
    completed: boolean,
    datetime: Date,
  }>,
};

function initModel(urls: {
  requestReport: string,
  reportResult: string,
  tasks: string,
}): void {
  model = {
    tasks: [],
    urls: {
      requestReport: urls.requestReport,
      reportResult: urls.reportResult,
      tasks: urls.tasks,
    },
  };
}

/**********/
/* update */
/**********/

function update(): void {
  getTasks();
}

function getTasks(): void {
  const url = model.urls.tasks;
  const req = buildReq({}, "get");

  fetch(url, req)
    .then(resp => resp.json())
    .then(data => {
      initTasks(data.tasks);
    });
}

function initTasks(
  data: Array<{
    task_id: string,
    description: string,
    completed: boolean,
    datetime: string,
  }>,
): void {
  model.tasks = data.map(task => ({
    id: task.task_id,
    description: task.description,
    completed: task.completed,
    datetime: new Date(task.datetime),
  }));
  const notifications = model.tasks.map(task => ({
    text: task.completed
      ? `Your report for ${task.description} is ready.`
      : `Computing report for ${task.description}...`,
    inProgress: !task.completed,
    onClick: () => downloadReport(task.id),
  }));
  initNotifications(notifications);
}

function requestReport(event): void {
  event.stopPropagation();
  const button = event.currentTarget;
  const group_id = button.getAttribute("data-group");
  const assignment_id = button.getAttribute("data-assignment");

  const data = {
    group_id: group_id,
    assignment_id: assignment_id,
  };

  const url = model.urls.requestReport;
  const req = buildReq(data, "post");

  fetch(url, req)
    .then(resp => resp.json())
    .then(data => {})
    .catch(err => {
      console.log(err);
    });
}

function downloadReport(taskId: string): void {}

/********/
/* view */
/********/

/*************/
/* listeners */
/*************/

function initListeners(): void {
  addReportListeners();
}

function addReportListeners(): void {
  [...document.getElementsByClassName("report-button")].forEach(button => {
    button.addEventListener("click", (event: MouseEvent) =>
      requestReport(event),
    );
  });
}

/********/
/* init */
/********/

export function init(urls: {
  requestReport: string,
  reportResult: string,
  tasks: string,
}): void {
  initModel(urls);
  update();
  initListeners();
}
