import { Component, h } from "preact";

import LinearProgress from "preact-material-components/LinearProgress";
import Snackbar from "preact-material-components/Snackbar";
import Select from "preact-material-components/Select";
import TextField from "preact-material-components/TextField";

import "preact-material-components/LinearProgress/style.css";
import "preact-material-components/List/style.css";
import "preact-material-components/Menu/style.css";
import "preact-material-components/Select/style.css";
import "preact-material-components/Snackbar/style.css";
import "preact-material-components/TextField/style.css";

import { get, submitData } from "./ajax.js";
import { QuestionCard, User } from "./question.js";

export class SearchDbApp extends Component {
  /* Expects a paginated response from server */
  state = {
    disciplines: [],
    questions: [],
    searching: false,
    searchTerms: "",
    selectedDiscipline: 0,
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
        });
      })
      .catch((error) => {
        console.error(error);
        this.bar.MDComponent.show({
          message: this.props.gettext(
            "An error occurred.  Try refreshing this page.",
          ),
        });
      });
  };

  handleOnChange = (evt) => {
    this.setState({ searchTerms: evt.target.value });
  };

  handleSubmit = (evt) => {
    if (evt.key === "Enter" && this.state.searchTerms != "") {
      this.setState({ searching: true, questions: [] }, () => {
        console.debug("Searching...");
        const queryString = new URLSearchParams({
          id: this.props.assignment,
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
            _this.setState({
              questions: data["results"].map((d, i) => {
                return {
                  question: d,
                  rank: i,
                };
              }),
              searching: false,
            });
          })
          .catch((error) => {
            console.error(error);
            this.bar.MDComponent.show({
              message: this.props.gettext(
                "An error occurred.  Try refreshing this page.",
              ),
            });
          });
      });
    }
  };

  add = async (pk) => {
    console.info({ assignment: this.props.assignment, question_pk: pk });
    try {
      await submitData(
        this.props.assignmentQuestionURL,
        { assignment: this.props.assignment, question_pk: pk },
        "POST",
      );
      this.bar.MDComponent.show({
        message: this.props.gettext("Item added."),
      });
      this.props.callback();
    } catch (error) {
      console.error(error);
      this.bar.MDComponent.show({
        message: this.props.gettext("An error occurred."),
      });
    }
  };

  searchBar = () => {
    if (this.state.searching) {
      return <LinearProgress indeterminate />;
    }
    return (
      <div>
        <Select
          hintText={this.props.gettext("Select a discipline")}
          selectedIndex={this.state.selectedDiscipline}
          onChange={(e) => {
            this.setState({
              selectedDiscipline: e.target.selectedIndex,
            });
          }}
          outlined
        >
          {this.state.disciplines.map((d) => (
            <Select.Item>{d.title}</Select.Item>
          ))}
        </Select>
        <TextField
          label={this.props.gettext("Type search terms")}
          helperText={this.props.gettext(
            "The search engine checks question texts for each keyword as well as the complete phrase.  You can also search on username to find all content from a certain contributor.  Search results are filtered to remove questions in your list of favourites and questions already part of this assignment.",
          )}
          helperTextPersistent
          value={this.state.searchTerms}
          onChange={this.handleOnChange}
          onKeyPress={this.handleSubmit}
        />
      </div>
    );
  };

  render() {
    return (
      <div>
        <User.Provider value={this.props.user}>
          {this.searchBar()}
          {this.state.questions.map((q) => (
            <QuestionCard
              cloneURL={this.props.questionCloneBaseURL}
              editURL={this.props.questionEditBaseURL}
              handleQuestionDelete={null}
              handleQuestionAdd={this.add}
              question={q.question}
              rank={null}
              gettext={this.props.gettext}
              showChoices={true}
              showImages={true}
              minimizeCards={false}
            />
          ))}
        </User.Provider>
        <Snackbar
          ref={(bar) => {
            this.bar = bar;
          }}
        />
      </div>
    );
  }
}
