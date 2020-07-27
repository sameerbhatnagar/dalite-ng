import { Component, h } from "preact";

import { LinearProgress } from "@rmwc/linear-progress";
import { Select, SelectHelperText } from "@rmwc/select";
import { Snackbar } from "@rmwc/snackbar";
import {
  TextField,
  TextFieldHelperText,
  TextFieldIcon,
} from "@rmwc/textfield";

import "@rmwc/linear-progress/node_modules/@material/linear-progress/dist/mdc.linear-progress.min.css";
import "@rmwc/snackbar/node_modules/@material/snackbar/dist/mdc.snackbar.min.css";
import "@rmwc/textfield/node_modules/@material/textfield/dist/mdc.textfield.min.css";
import "@rmwc/textfield/node_modules/@material/floating-label/dist/mdc.floating-label.min.css";
import "@rmwc/textfield/node_modules/@material/notched-outline/dist/mdc.notched-outline.min.css";
import "@rmwc/textfield/node_modules/@material/line-ripple/dist/mdc.line-ripple.min.css";
import "@rmwc/select/node_modules/@material/select/dist/mdc.select.min.css";

import { get, submitData } from "./ajax.js";
import { QuestionCard, User } from "./question.js";

export class SearchDbApp extends Component {
  /* Expects a paginated response from server */
  state = {
    disciplines: [],
    questions: [],
    searching: false,
    searchTerms: "",
    selectedDiscipline: this.props.defaultDiscipline,
    snackbarIsOpen: false,
    snackbarMessage: "",
  };

  componentDidMount() {
    this.refreshFromDB();
  }

  refreshFromDB = () => {
    const _this = this;
    const _disciplines = get(this.props.disciplineURL);
    _disciplines
      .then((data) => {
        console.debug(data);
        _this.setState({
          disciplines: data,
          selectedDiscipline: this.props.defaultDiscipline,
        });
      })
      .catch((error) => {
        console.error(error);
        this.setState({
          snackbarIsOpen: true,
          snackbarMessage: this.props.gettext(
            "An error occurred.  Try refreshing this page.",
          ),
        });
      });
  };

  handleSubmit = (evt) => {
    if (evt.key === "Enter" && this.state.searchTerms != "") {
      this.setState({ searching: true, questions: [] }, () => {
        console.debug("Searching...");
        const queryString = new URLSearchParams({
          assignment_id: this.props.assignment,
          limit_search: false,
          type: this.props.type,
          search_string: this.state.searchTerms,
        });
        const url = `${this.props.searchURL}?${queryString.toString()}`;
        const _this = this;
        const _questions = get(url);
        _questions
          .then((data) => {
            console.debug(data);
            if (data["count"] > 0) {
              _this.setState({
                questions: data["results"].map((d, i) => {
                  return {
                    question: d,
                    rank: i,
                  };
                }),
                searching: false,
              });
            } else {
              this.setState({
                searching: false,
                snackbarIsOpen: true,
                snackbarMessage: this.props.gettext(
                  "No questions match query.",
                ),
              });
            }
          })
          .catch((error) => {
            console.error(error);
            this.setState({
              snackbarIsOpen: true,
              snackbarMessage: this.props.gettext(
                "An error occurred.  Try refreshing this page.",
              ),
            });
          });
      });
    }
  };

  add = async (pk, i) => {
    try {
      await submitData(
        this.props.assignmentQuestionURL,
        { assignment: this.props.assignment, question_pk: pk },
        "POST",
      );
      const _questions = this.state.questions;
      _questions.splice(i, 1);
      this.setState({
        questions: _questions,
        snackbarIsOpen: true,
        snackbarMessage: this.props.gettext("Item added."),
      });
      this.props.callback();
    } catch (error) {
      console.error(error);
      this.setState({
        snackbarIsOpen: true,
        snackbarMessage: this.props.gettext("An error occurred."),
      });
    }
  };

  searchBar = () => {
    if (this.state.searching) {
      return <LinearProgress determinate={false} />;
    }
    return (
      <div>
        <div style={{ marginBottom: "20px" }}>
          <TextField
            withLeadingIcon={<TextFieldIcon icon="search" theme="secondary" />}
            withTrailingIcon={
              <TextFieldIcon
                tabIndex="0"
                icon="close"
                onClick={() => this.setState({ searchTerms: "" })}
                theme="primary"
                style={
                  this.state.searchTerms.length > 0
                    ? {}
                    : { opacity: "0", pointerEvents: "none" }
                }
              />
            }
            label={this.props.gettext("Type search terms")}
            value={this.state.searchTerms}
            onInput={(evt) => {
              this.setState({ searchTerms: evt.target.value });
            }}
            onKeyPress={this.handleSubmit}
            theme="secondary"
          />
          <TextFieldHelperText persistent>
            {this.props.gettext(
              "The search engine checks question texts for each keyword as well as the complete phrase.  You can also search on username to find all content from a certain contributor.  Search results are filtered to remove questions in your list of favourites and questions already part of this assignment.",
            )}
          </TextFieldHelperText>
        </div>
        <div style={{ marginBottom: "20px" }}>
          <Select
            value={this.state.selectedDiscipline}
            onChange={(e) => {
              console.info(this.state.selectedDiscipline);
              console.info(e.target);
              this.setState({
                selectedDiscipline: e.target.value,
              });
            }}
            outlined
            options={this.state.disciplines.map((d) => {
              return { label: d.title, value: d.pk };
            })}
            style={{ appearance: "none" }}
          />
          <SelectHelperText persistent>
            {this.props.gettext(
              "Search results will only include questions in the selected discipline.",
            )}
          </SelectHelperText>
        </div>
      </div>
    );
  };

  render() {
    return (
      <div>
        <User.Provider value={this.props.user}>
          {this.searchBar()}
          {this.state.questions.map((q, i) => (
            <QuestionCard
              cloneURL={this.props.questionCloneBaseURL}
              editURL={this.props.questionEditBaseURL}
              handleQuestionDelete={null}
              handleQuestionAdd={this.add}
              question={q.question}
              rank={i}
              gettext={this.props.gettext}
              showChoices={true}
              showImages={true}
              minimizeCards={false}
            />
          ))}
        </User.Provider>
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
