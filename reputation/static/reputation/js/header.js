"use strict";

export { init as studentInit } from "./_header/student.js";
import { TeacherReputationHeader } from "./_header/teacher.js";

if (!customElements.get("teacher-reputation-header")) {
  customElements.define("teacher-reputation-header", TeacherReputationHeader);
}
