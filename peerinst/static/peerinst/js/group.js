export {editField, saveField} from './_group/common.js';
export {removeAssignment} from './_group/details.js';
import {
  setUpAssignmentPage,
  saveQuestionList,
  sendAssignmentEmail,
} from './_group/assignment.js';
setUpAssignmentPage();
export {saveQuestionList, sendAssignmentEmail};
