import { Component, h, render } from "preact";
import Card from "preact-material-components/Card";
import "preact-material-components/Card/style.css";
import "preact-material-components/Button/style.css";
import IconToggle from "preact-material-components/IconToggle";
import Checkbox from "preact-material-components/Checkbox";
import Formfield from "preact-material-components/FormField";
import "preact-material-components/Checkbox/style.css";

export { h, render };

/*
function getCsrfToken() {
  return document.querySelectorAll("input[name=csrfmiddlewaretoken]")[0].value;
}
*/

async function handleResponse(response) {
  const data = await response.json();

  if (response.status == 200 || response.status == 201) {
    return data;
  }

  if (response.status == 401) {
    const base = new URL(window.location.protocol + window.location.host);
    const url = new URL(data["login_url"], base);
    url.search = `?next=${window.location.pathname}`;
    console.debug(url);
    window.location.href = url;
  }

  if (response.status == 403) {
    // Could raise an alert??
    return data;
  }
}

async function get(url) {
  const response = await fetch(url, {
    method: "GET",
    mode: "same-origin",
    cache: "no-cache",
    credentials: "same-origin",
    redirect: "follow",
    referrer: "client",
  });

  return await handleResponse(response);
}

class ToggleVisibleItems extends Component {
  render() {
    return (
      <div>
        <Formfield className="mdc-theme--secondary">
          <label for="toggle-images">
            {this.props.gettext("Show images")}
          </label>
          <Checkbox
            id="toggle-images"
            checked={this.props.showImages}
            onclick={this.props.handleImageToggleClick}
          />
        </Formfield>
        <Formfield className="mdc-theme--secondary">
          <label for="toggle-answers">
            {this.props.gettext("Show choices")}
          </label>
          <Checkbox
            id="toggle-answers"
            checked={this.props.showChoices}
            onclick={this.props.handleAnswerToggleClick}
          />
        </Formfield>
      </div>
    );
  }
}

class Image extends Component {
  render() {
    if (this.props.url) {
      return (
        <img
          class="mdc-typography--caption question-image"
          src={this.props.url}
          alt={this.props.altText}
          style={{ display: this.props.show ? "block" : "none" }}
        />
      );
    }
  }
}

const Checkmark = (props) => {
  if (props.correct) {
    return <i class="check material-icons">check</i>;
  }
};

class Choices extends Component {
  choiceList = () => {
    return this.props.choices.map((choice) => {
      return (
        <li class="dense-list">
          {/* eslint-disable-next-line */}
          {choice[0]}. <span dangerouslySetInnerHTML={{ __html: choice[1] }} />{" "}
          <Checkmark correct={choice[2]} />
        </li>
      );
    });
  };

  render() {
    if (this.props.show) {
      return <ul>{this.choiceList()}</ul>;
    }
  }
}

class QuestionCard extends Component {
  renderCategory = () => {
    if (this.props.question.category) {
      return this.props.question.category.map((el, index) =>
        index > 0 ? `, ${el.title}` : el.title,
      );
    }
    return this.props.gettext("Uncategorized");
  };

  render() {
    return (
      <div>
        <Card>
          <div className="card-header">
            <div
              className="mdc-typography--title bold"
              // eslint-disable-next-line
              dangerouslySetInnerHTML={{ __html: this.props.question.title }}
            />
            <div class="mdc-typography--caption">
              #{this.props.question.pk} {this.props.gettext("by")}{" "}
              {this.props.question.user.username}
            </div>
            <div
              className="mdc-typography--body1 m-top-5"
              // eslint-disable-next-line
              dangerouslySetInnerHTML={{ __html: this.props.question.text }}
            />
          </div>
          <Image
            show={this.props.showImages}
            url={this.props.question.image}
            altText={this.props.question.image_alt_text}
          />
          <Choices
            show={this.props.showChoices}
            choices={this.props.question.choices}
          />
          <Card.Media className="card-media" />
          <Card.Actions>
            <Card.ActionButtons className="mdc-card__action-buttons grey">
              <div class="mdc-typography--caption">
                <div>
                  {this.props.gettext("Discipline")}:{" "}
                  {this.props.question.discipline.title}
                </div>
                <div>
                  {this.props.gettext("Categories")}: {this.renderCategory()}
                </div>
                <div>
                  {this.props.gettext("Student answers")}:{" "}
                  {this.props.question.answer_count}
                </div>
              </div>
            </Card.ActionButtons>
            <Card.ActionIcons>
              <IconToggle className="mdc-theme--primary">
                assessment
              </IconToggle>
              <IconToggle className="mdc-theme--primary">file_copy</IconToggle>
              <IconToggle className="mdc-theme--primary">delete</IconToggle>
            </Card.ActionIcons>
          </Card.Actions>
        </Card>
      </div>
    );
  }
}

export class AssignmentUpdateApp extends Component {
  state = {
    showChoices: sessionStorage.answers == "block",
    showImages: sessionStorage.images == "block",
    questions: [],
  };

  handleImageToggleClick = () => {
    this.setState({ showImages: !this.state.showImages }, () => {
      sessionStorage.images = this.state.showImages ? "block" : "none";
    });
  };

  handleAnswerToggleClick = () => {
    this.setState({ showChoices: !this.state.showChoices }, () => {
      sessionStorage.answers = this.state.showChoices ? "block" : "none";
    });
  };

  refreshFromDB = () => {
    const _this = this;
    const _questions = get(this.props.assignmentURL);
    _questions
      .then((data) => {
        console.debug(data);
        _this.setState({
          questions: data["questions"],
        });
      })
      .catch((error) => console.error(error));
  };

  questionList = () => {
    return this.state.questions.map((q) => {
      return (
        <QuestionCard
          question={q.question}
          gettext={this.props.gettext}
          showChoices={this.state.showChoices}
          showImages={this.state.showImages}
        />
      );
    });
  };

  componentDidMount() {
    this.refreshFromDB();
  }

  render() {
    return (
      <div>
        <ToggleVisibleItems
          gettext={this.props.gettext}
          showChoices={this.state.showChoices}
          showImages={this.state.showImages}
          handleAnswerToggleClick={this.handleAnswerToggleClick}
          handleImageToggleClick={this.handleImageToggleClick}
        />
        <div>{this.questionList()}</div>
      </div>
    );
  }
}
