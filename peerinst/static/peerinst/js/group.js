export {editField, saveField} from './_group/common.js';
export {removeAssignment} from './_group/details.js';
import {
  addAssignmentEventListeners,
  saveQuestionList,
} from './_group/assignment.js';
addAssignmentEventListeners();
export {saveQuestionList};
