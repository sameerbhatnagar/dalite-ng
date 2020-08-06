import { Component, Fragment, h } from "preact";

import {
  DataTable,
  DataTableContent,
  DataTableHead,
  DataTableBody,
  DataTableHeadCell,
  DataTableRow,
  DataTableCell,
} from "@rmwc/data-table";
import { Snackbar } from "@rmwc/snackbar";
import { TextField } from "@rmwc/textfield";

import "@rmwc/data-table/data-table.css";
import "@rmwc/snackbar/node_modules/@material/snackbar/dist/mdc.snackbar.min.css";
import "@rmwc/textfield/node_modules/@material/textfield/dist/mdc.textfield.css";

import { get } from "../_assignment/ajax.js";

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
    return (
      <div>
        <DataTable stickyRows="1" style={{ width: "775px" }}>
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
                    <DataTableCell
                      alignStart
                      style={{ minWidth: "130px", whiteSpace: "normal" }}
                    >
                      {/* eslint-disable-next-line */}
                      <span
                        dangerouslySetInnerHTML={{
                          __html: answer.answer_choice.text,
                        }}
                      />
                    </DataTableCell>
                    <DataTableCell alignStart style={{ whiteSpace: "normal" }}>
                      {answer.rationale}
                    </DataTableCell>
                    <DataTableCell
                      style={{ minWidth: "200px", whiteSpace: "normal" }}
                    >
                      <TextField />
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
