"use strict";

import { TeacherReputationHeader } from "./_header/teacher.js";

if (!customElements.get("teacher-reputation-header")) {
  customElements.define("teacher-reputation-header", TeacherReputationHeader);
}
