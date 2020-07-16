import { Component, h, render } from "preact";
import Card from "preact-material-components/Card";
import "preact-material-components/Card/style.css";
import "preact-material-components/Button/style.css";
import IconToggle from "preact-material-components/IconToggle";

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

class QuestionCard extends Component {
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
          <Card.Media className="card-media" />
          <Card.Actions>
            <Card.ActionButtons className="mdc-card__action-buttons grey">
              <div class="mdc-typography--caption">
                <div>
                  {this.props.gettext("Discipline")}:{" "}
                  {this.props.question.discipline.title}
                </div>

                <div>
                  {this.props.gettext("Student answers")}:{" "}
                  {this.props.question.answer_count}
                </div>
              </div>
            </Card.ActionButtons>
            <Card.ActionIcons>
              <IconToggle>share</IconToggle>
            </Card.ActionIcons>
          </Card.Actions>
        </Card>
      </div>
    );
  }
}

export class AssignmentUpdateApp extends Component {
  state = {
    questions: [],
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
        <QuestionCard question={q.question} gettext={this.props.gettext} />
      );
    });
  };

  componentDidMount() {
    this.refreshFromDB();
  }

  render() {
    return <div>{this.questionList()}</div>;
  }
}
