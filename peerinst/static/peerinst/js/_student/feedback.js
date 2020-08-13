import { Component } from "preact";

import { LinearProgress } from "@rmwc/linear-progress";
import { Snackbar } from "@rmwc/snackbar";

import "@rmwc/linear-progress/node_modules/@material/linear-progress/dist/mdc.linear-progress.min.css";
import "@rmwc/snackbar/node_modules/@material/snackbar/dist/mdc.snackbar.min.css";

import { get } from "../_ajax/ajax.js";

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
    );
  }
}
