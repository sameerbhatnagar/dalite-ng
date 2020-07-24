import { Component, h } from "preact";

import Checkbox from "preact-material-components/Checkbox";
import Formfield from "preact-material-components/FormField";
import LinearProgress from "preact-material-components/LinearProgress";
import Snackbar from "preact-material-components/Snackbar";
import TextField from "preact-material-components/TextField";

import "preact-material-components/Checkbox/style.css";
import "preact-material-components/LinearProgress/style.css";
import "preact-material-components/Snackbar/style.css";
import "preact-material-components/TextField/style.css";

import { get, submitData } from "./ajax.js";
import { QuestionCard, User } from "./question.js";

export class SearchDbApp extends Component {
  state = {
    limitSearch: true,
    questions: [],
    searching: false,
    searchTerms: "",
  };

  handleOnChange = (evt) => {
    this.setState({ searchTerms: evt.target.value });
  };

  handleSubmit = (evt) => {
    if (evt.key === "Enter" && this.state.searchTerms != "") {
      this.setState({ searching: true }, () => {
        console.debug("Searching...");
        const queryString = new URLSearchParams({
          id: this.props.assignment,
          limit_search: this.state.limitSearch,
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
              questions: data.map((d, i) => {
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
        <Formfield className="mdc-theme--secondary">
          <Checkbox
            aria-label={this.props.gettext(
              "Click to limit question search to your discipline(s)",
            )}
            checked={this.state.limitSearch}
            id="limit-search"
            onclick={(e) =>
              this.setState({ limitSearch: !this.state.limitSearch })
            }
            title={this.props.gettext(
              "Click to limit question search to your discipline(s)",
            )}
          />
          <label for="limit-search">
            {this.props.gettext(
              "Limit search to questions in your discipline(s) (recommended)?",
            )}
          </label>
        </Formfield>
        <div>
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
