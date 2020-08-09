import moment from "moment";
import { Component, Fragment, h } from "preact";

import { CircularProgress } from "@rmwc/circular-progress";
import {
  DataTable,
  DataTableContent,
  DataTableHead,
  DataTableBody,
  DataTableHeadCell,
  DataTableRow,
  DataTableCell,
} from "@rmwc/data-table";
import { Dialog, DialogContent } from "@rmwc/dialog";
import { IconButton } from "@rmwc/icon-button";
import { LinearProgress } from "@rmwc/linear-progress";
import { Snackbar } from "@rmwc/snackbar";
import { TextField } from "@rmwc/textfield";
import { Typography } from "@rmwc/typography";

import "@rmwc/button/node_modules/@material/button/dist/mdc.button.css";
import "@rmwc/circular-progress/circular-progress.css";
import "@rmwc/data-table/data-table.css";
import "@rmwc/dialog/node_modules/@material/dialog/dist/mdc.dialog.css";
import "@rmwc/icon-button/node_modules/@material/icon-button/dist/mdc.icon-button.min.css";
import "@rmwc/linear-progress/node_modules/@material/linear-progress/dist/mdc.linear-progress.min.css";
import "@rmwc/snackbar/node_modules/@material/snackbar/dist/mdc.snackbar.min.css";
import "@rmwc/textfield/node_modules/@material/textfield/dist/mdc.textfield.css";
import "@rmwc/theme/node_modules/@material/theme/dist/mdc.theme.min.css";
import "@rmwc/typography/node_modules/@material/typography/dist/mdc.typography.min.css";

import { get, submitData } from "../_assignment/ajax.js";

class AnswerFeedback extends Component {
  state = {
    changed: false,
    create: true,
    loaded: false,
    note: "",
    saving: false,
    score: null,
    score_hover: null,
    snackbarIsOpen: false,
    snackbarMessage: "",
  };

  scores = Array.from([1, 2, 3]);
  annotations = Array.from([
    this.props.gettext("Not convincing"),
    this.props.gettext("Somewhat convincing"),
    this.props.gettext("Very convincing"),
  ]);

  refreshFromDB = async () => {
    // Load answer annotation instance
    try {
      const data = await get(
        `${this.props.feedbackURL}through_answer/${this.props.pk}/`,
      );
      console.debug(data);
      this.setState({
        create: false,
        loaded: true,
        note: data["note"] ? data["note"] : "",
        score: data["score"],
      });
    } catch (error) {
      // Ignore 404s
      this.setState({
        loaded: true,
      });
    }
  };

  save = async (score) => {
    this.setState({ saving: true });
    try {
      if (!this.state.create) {
        // Object exists, so PATCH
        const data = await submitData(
          `${this.props.feedbackURL}through_answer/${this.props.pk}/`,
          { note: this.state.note, score },
          "PATCH",
        );
        console.info(data);
      } else {
        // Object doesn't exist, so POST
        const data = await submitData(
          this.props.feedbackURL,
          {
            answer: this.props.pk,
            note: this.state.note,
            score,
          },
          "POST",
        );
        console.info(data);
      }
      this.setState({
        changed: false,
        create: false,
        saving: false,
        score,
        score_hover: null,
        snackbarIsOpen: true,
        snackbarMessage: this.props.gettext("Saved"),
      });
    } catch (error) {
      console.error(error);
      this.setState({
        saving: false,
        snackbarIsOpen: true,
        snackbarMessage: this.props.gettext(
          "An error occurred.  Try refreshing this page.",
        ),
      });
    }
  };

  saveInProgress = () => {
    if (this.state.saving) {
      return (
        <div style={{ position: "absolute ", bottom: "-5px" }}>
          <Typography use="caption">
            {this.props.gettext("Saving...")}
          </Typography>
        </div>
      );
    }
  };

  componentDidMount() {
    this.refreshFromDB();
  }

  render() {
    if (!this.state.loaded) {
      return <CircularProgress size="xlarge" />;
    }
    return (
      <div style={{ position: "relative" }}>
        <TextField
          textarea
          fullwidth
          rows="3"
          label="Comments"
          dense
          value={this.state.note}
          onInput={(evt) => {
            this.setState({ changed: true, note: evt.target.value });
          }}
          onBlur={() => {
            if (this.state.changed) {
              this.save(this.state.score);
            }
          }}
        />

        <IconButton
          icon="outlined_flag"
          checked={
            (this.state.score == 0 && this.state.score_hover == null) ||
            (this.state.score != 0 && this.state.score_hover == 0)
          }
          onClick={() =>
            this.state.score != 0 ? this.save(0) : this.save(null)
          }
          onIcon="flag"
          onMouseEnter={() => {
            this.setState({ score_hover: 0 });
          }}
          onMouseOut={() => {
            this.setState({ score_hover: null });
          }}
          theme="primary"
          title={this.props.gettext("Never show")}
        />

        {this.scores.map((score, i) => {
          return (
            <IconButton
              icon="star_border"
              checked={
                (this.state.score >= score &&
                  this.state.score_hover >= score) ||
                (this.state.score >= score &&
                  this.state.score_hover == null) ||
                (this.state.score != score && this.state.score_hover >= score)
              }
              onClick={() => this.save(score)}
              onIcon="star"
              onMouseEnter={() => {
                this.setState({ score_hover: score });
              }}
              onMouseOut={() => {
                this.setState({ score_hover: null });
              }}
              theme="primary"
              title={this.annotations[i]}
            />
          );
        })}

        {this.saveInProgress()}

        <Snackbar
          show={this.state.snackbarIsOpen}
          onHide={(evt) => this.setState({ snackbarIsOpen: false })}
          message={this.state.snackbarMessage}
          timeout={1000}
          actionHandler={() => {}}
          actionText="OK"
          dismissesOnAction={true}
          style={{ zIndex: 1000 }}
          alignStart
        />
      </div>
    );
  }
}

export class RationaleTableApp extends Component {
  state = {
    answers: [],
    answersNatural: [],
    loaded: false,
    snackbarIsOpen: false,
    snackbarMessage: "",
  };

  refreshFromDB = async (url = this.props.readURL) => {
    // Load answer data
    this.setState({ loaded: false });
    try {
      const data = await get(url);
      console.debug(data);
      this.setState({
        answers: data["answers"],
        answersNatural: data["answers"],
        loaded: true,
      });
    } catch (error) {
      console.error(error);
      this.setState({
        snackbarIsOpen: true,
        snackbarMessage: this.props.gettext(
          "An error occurred.  Try refreshing this page.",
        ),
      });
    }
  };

  componentDidMount() {
    this.refreshFromDB();
  }

  shouldComponentUpdate(nextProps, nextState) {
    if (this.props.readURL != nextProps.readURL) {
      this.refreshFromDB(nextProps.readURL);
    }
    return true;
  }

  render() {
    if (!this.state.loaded) {
      return <LinearProgress determinate={false} style={{ width: "775px" }} />;
    }
    return (
      <div>
        <Dialog
          open={this.props.dialogIsOpen}
          onClose={() => this.props.listener()}
        >
          <DialogContent>
            <DataTable stickyRows="1" style={{ width: "800px" }}>
              <DataTableContent>
                <DataTableHead>
                  <DataTableRow>
                    <DataTableHeadCell
                      alignEnd
                      sort={this.state.sortDir || null}
                      onSortChange={(sortDir) => {
                        if (sortDir) {
                          const _answers = Array.from(this.state.answers);
                          _answers.sort((a, b) =>
                            a.user_email.localeCompare(b.user_email) < 0
                              ? sortDir * 1
                              : sortDir * -1,
                          );
                          this.setState({ sortDir, answers: _answers });
                        } else {
                          this.setState({
                            sortDir,
                            answers: this.state.answersNatural,
                          });
                        }
                      }}
                    >
                      <span style={{ textDecoration: "underline" }}>User</span>
                    </DataTableHeadCell>
                    <DataTableHeadCell>1st</DataTableHeadCell>
                    <DataTableHeadCell alignStart>Rationale</DataTableHeadCell>
                    <DataTableHeadCell>2nd</DataTableHeadCell>
                    <DataTableHeadCell>Chosen rationale</DataTableHeadCell>
                    <DataTableHeadCell alignStart>Feedback</DataTableHeadCell>
                  </DataTableRow>
                </DataTableHead>
                <DataTableBody>
                  {this.state.answers.map((answer) => (
                    <Fragment>
                      <DataTableRow>
                        <DataTableCell alignEnd>
                          {answer.user_email.substring(0, 10)}
                        </DataTableCell>
                        <DataTableCell alignMiddle>
                          {answer.first_answer_choice}
                        </DataTableCell>
                        <DataTableCell
                          alignStart
                          style={{ whiteSpace: "normal" }}
                        >
                          <Typography use="body2">
                            {answer.rationale}
                          </Typography>
                          <div>
                            <Typography use="caption" theme="primary">
                              {moment(answer.datetime_start).format(
                                "MM/DD/YY LT",
                              )}
                            </Typography>
                          </div>
                        </DataTableCell>
                        <DataTableCell alignMiddlet>
                          {answer.second_answer_choice}
                        </DataTableCell>
                        <DataTableCell
                          alignStart
                          style={{ whiteSpace: "normal" }}
                        >
                          <Typography use="body2">
                            {answer.chosen_rationale}
                          </Typography>
                        </DataTableCell>
                        <DataTableCell
                          style={{ minWidth: "250px", whiteSpace: "normal" }}
                        >
                          <AnswerFeedback
                            feedbackURL={this.props.feedbackURL}
                            gettext={this.props.gettext}
                            pk={answer.id}
                          />
                        </DataTableCell>
                      </DataTableRow>
                    </Fragment>
                  ))}
                </DataTableBody>
              </DataTableContent>
            </DataTable>
          </DialogContent>
        </Dialog>
        <Snackbar
          show={this.state.snackbarIsOpen}
          onHide={(evt) => this.setState({ snackbarIsOpen: false })}
          message={this.state.snackbarMessage}
          timeout={5000}
          actionHandler={() => {}}
          actionText="OK"
          dismissesOnAction={true}
          alignStart
        />
      </div>
    );
  }
}
