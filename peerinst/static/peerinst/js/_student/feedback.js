import { Component, Fragment, h } from "preact";

import {
  Dialog,
  DialogActions,
  DialogButton,
  DialogContent,
} from "@rmwc/dialog";
import { LinearProgress } from "@rmwc/linear-progress";
import { Snackbar } from "@rmwc/snackbar";
import { Typography } from "@rmwc/typography";

import "@rmwc/button/node_modules/@material/button/dist/mdc.button.css";
import "@rmwc/dialog/node_modules/@material/dialog/dist/mdc.dialog.css";
import "@rmwc/linear-progress/node_modules/@material/linear-progress/dist/mdc.linear-progress.min.css";
import "@rmwc/snackbar/node_modules/@material/snackbar/dist/mdc.snackbar.min.css";
import "@rmwc/typography/node_modules/@material/typography/dist/mdc.typography.min.css";

import { get } from "../_ajax/ajax.js";
import { Choices } from "../_assignment/question.js";

class Feedback extends Component {
  insertSummary = () => {
    if (this.props.feedback.answer.answer_choice.text) {
      return (
        <Fragment>
          <blockquote
            // eslint-disable-next-line
            dangerouslySetInnerHTML={{
              __html: this.props.feedback.answer.answer_choice.text,
            }}
          />
          <p>
            <strong>{this.props.gettext("because")}</strong>
          </p>
          <blockquote>{this.props.feedback.answer.rationale}</blockquote>
        </Fragment>
      );
    }
    return <blockquote>{this.props.feedback.answer.rationale}</blockquote>;
  };

  render() {
    return (
      <div style={{ marginTop: "14px", paddingBottom: "4px" }}>
        <Typography use="headline5">
          <div
            // eslint-disable-next-line
            dangerouslySetInnerHTML={{
              __html: this.props.feedback.answer.question.title,
            }}
            style={{ marginBottom: "12px" }}
          />
        </Typography>
        <Typography use="body1">
          <div
            // eslint-disable-next-line
            dangerouslySetInnerHTML={{
              __html: this.props.feedback.answer.question.text,
            }}
          />
        </Typography>
        <Choices
          show={true}
          choices={this.props.feedback.answer.question.choices}
        />

        <div style={{ marginTop: "16px" }}>
          <Typography use="body1">
            <p>
              <strong>{this.props.gettext("You thought:")}</strong>
            </p>
            {this.insertSummary()}
            <p>
              <strong>{this.props.gettext("Your teacher commented:")}</strong>
            </p>
            <blockquote>{this.props.feedback.note}</blockquote>
          </Typography>
          <Typography use="headline4" theme="primary">
            <p style={{ paddingRight: "40px", textAlign: "right" }}>
              {this.props.feedback.score}/3
            </p>
          </Typography>
        </div>
      </div>
    );
  }
}

export class FeedbackApp extends Component {
  state = {
    loaded: false,
    feedback: [],
    snackbarIsOpen: false,
    snackbarMessage: "",
  };

  refreshFromDB = async () => {
    // Load answer data
    this.setState({ loaded: false });
    try {
      const data = await get(this.props.feedbackURL);
      console.debug(data);
      this.setState(
        {
          feedback: data,
          loaded: true,
        },
        this.props.callback(
          Array.from(new Set(data.map((el) => el.answer.assignment))),
        ),
      );
    } catch (error) {
      console.error(error);
      this.setState({
        loaded: true,
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
      return <LinearProgress determinate={false} style={{ width: "775px" }} />;
    }
    const feedbackList = this.state.feedback.filter(
      (el) => el.answer.assignment == this.props.assignmentId,
    );
    return (
      <div>
        <Dialog
          open={this.props.dialogIsOpen}
          onClose={() => this.props.listener()}
        >
          <DialogContent
            style={{
              display: "flex",
              flexDirection: "column",
            }}
          >
            <div style={{ maxWidth: "775px" }}>
              {feedbackList.map((el) => (
                <Feedback feedback={el} gettext={this.props.gettext} />
              ))}
            </div>
          </DialogContent>
          <DialogActions>
            <DialogButton action="accept" isDefaultAction theme="primary">
              {this.props.gettext("Done")}
            </DialogButton>
          </DialogActions>
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
