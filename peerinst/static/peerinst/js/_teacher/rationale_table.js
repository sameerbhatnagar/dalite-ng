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
import { IconButton } from "@rmwc/icon-button";
import { LinearProgress } from "@rmwc/linear-progress";
import { Snackbar } from "@rmwc/snackbar";
import { TextField } from "@rmwc/textfield";
import { Typography } from "@rmwc/typography";

import "@rmwc/circular-progress/circular-progress.css";
import "@rmwc/data-table/data-table.css";
import "@rmwc/icon-button/node_modules/@material/icon-button/dist/mdc.icon-button.min.css";
import "@rmwc/linear-progress/node_modules/@material/linear-progress/dist/mdc.linear-progress.min.css";
import "@rmwc/snackbar/node_modules/@material/snackbar/dist/mdc.snackbar.min.css";
import "@rmwc/textfield/node_modules/@material/textfield/dist/mdc.textfield.css";
import "@rmwc/theme/node_modules/@material/theme/dist/mdc.theme.min.css";
import "@rmwc/typography/node_modules/@material/typography/dist/mdc.typography.min.css";

import { get, submitData } from "../_assignment/ajax.js";

class AnswerFeedback extends Component {
  state = {
    create: true,
    loaded: false,
    note: "",
    score: null,
  };

  scores = Array.from([1, 2, 3]);

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
    console.info("Saving");
    try {
      if (!this.state.create) {
        // Object exists, so PATCH
        await submitData(
          `${this.props.feedbackURL}through_answer/${this.props.pk}/`,
          { note: this.state.note, score },
          "PATCH",
        );
      } else {
        // Object doesn't exist, so POST
        await submitData(
          this.props.feedbackURL,
          {
            answer: this.props.pk,
            note: this.state.note,
            score,
          },
          "POST",
        );
      }
      this.setState({
        create: false,
        score,
      });
    } catch (error) {
      console.error(error);
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
      <Fragment>
        <TextField
          textarea
          fullwidth
          rows="3"
          label="Comments"
          dense
          value={this.state.note}
          onChange={(evt) => {
            this.setState({ note: evt.target.value });
          }}
          onBlur={() => this.save(this.state.score)}
        />

        <IconButton
          icon="outlined_flag"
          checked={this.state.score == 0}
          onClick={() => this.save(0)}
          onIcon="flag"
          theme="primary"
        />

        {this.scores.map((score) => {
          return (
            <IconButton
              icon="star_border"
              checked={this.state.score >= score}
              onClick={() => this.save(score)}
              onIcon="star"
              theme="primary"
            />
          );
        })}
      </Fragment>
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

  refreshFromDB = async () => {
    // Load answer data
    try {
      const data = await get(this.props.readURL);
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

  render() {
    if (!this.state.loaded) {
      return <LinearProgress determinate={false} />;
    }
    return (
      <div>
        <DataTable stickyRows="1" style={{ width: "850px" }}>
          <DataTableContent>
            <DataTableHead>
              <DataTableRow>
                <DataTableHeadCell
                  alignStart
                  sort={this.state.sortDir || null}
                  onSortChange={(sortDir) => {
                    console.log(sortDir);
                    if (sortDir) {
                      const _answers = Array.from(this.state.answers);
                      _answers.sort((a, b) =>
                        a.user_token.localeCompare(b.user_token) < 0
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
                  User
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
                    <DataTableCell alignStart>
                      {answer.user_token.substring(0, 10)}
                    </DataTableCell>
                    <DataTableCell alignMiddle>
                      {answer.first_answer_choice}
                    </DataTableCell>
                    <DataTableCell alignStart style={{ whiteSpace: "normal" }}>
                      <Typography use="body2">{answer.rationale}</Typography>
                    </DataTableCell>
                    <DataTableCell alignMiddlet>
                      {answer.second_answer_choice}
                    </DataTableCell>
                    <DataTableCell alignStart style={{ whiteSpace: "normal" }}>
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
        <Snackbar
          show={this.state.snackbarIsOpen}
          onHide={(evt) => this.setState({ snackbarIsOpen: false })}
          message={this.state.snackbarMessage}
          timeout={5000}
          actionHandler={() => {}}
          actionText="OK"
          dismissesOnAction={true}
        />
      </div>
    );
  }
}
