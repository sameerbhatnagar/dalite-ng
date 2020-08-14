import { Component, h } from "preact";

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
  render() {
    return (
      <div style={{ marginTop: "12px", marginBottom: "4px" }}>
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
        <Typography use="body1">
          <p>
            {this.props.gettext("You thought '") +
              this.props.feedback.answer.answer_choice.text +
              this.props.gettext("' because '") +
              this.props.feedback.answer.rationale}
          </p>
        </Typography>

        <Typography use="body1">
          <p>
            {this.props.gettext("Your teacher commented: ") +
              this.props.feedback.note}
          </p>
        </Typography>
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
      this.setState({
        feedback: data,
        loaded: true,
      });
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
            <div style={{ padding: "16px 0px", maxWidth: "775px" }}>
              <Typography use="headline5" theme="secondary">
                {this.props.assignmentTitle}
              </Typography>

              {this.state.feedback
                .filter(
                  (el) => el.answer.assignment == this.props.assignmentId,
                )
                .map((el) => (
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
