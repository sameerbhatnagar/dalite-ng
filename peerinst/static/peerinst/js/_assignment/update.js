import { Component, h, render } from "preact";
import Card from "preact-material-components/Card";
import "preact-material-components/Card/style.css";
import "preact-material-components/Button/style.css";
//import IconToggle from "preact-material-components/IconToggle";
import Checkbox from "preact-material-components/Checkbox";
import Formfield from "preact-material-components/FormField";
import "preact-material-components/Checkbox/style.css";
import { DragDropContext, Draggable, Droppable } from "react-beautiful-dnd";

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
          <label for="toggle-minimize">
            {this.props.gettext("Reorder questions?")}
          </label>
          <Checkbox
            id="toggle-minimize"
            checked={this.props.minimizeCards}
            onclick={this.props.handleMinimizeToggleClick}
          />
        </Formfield>
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
            onclick={this.props.handleChoiceToggleClick}
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

  cardBody = () => {
    if (!this.props.minimizeCards) {
      return (
        <div>
          <div
            className="mdc-typography--body1 m-top-5"
            // eslint-disable-next-line
            dangerouslySetInnerHTML={{ __html: this.props.question.text }}
          />
          <Image
            show={this.props.showImages}
            url={this.props.question.image}
            altText={this.props.question.image_alt_text}
          />
          <Choices
            show={this.props.showChoices}
            choices={this.props.question.choices}
          />
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
              {/*
              <IconToggle>assessment</IconToggle>
              <IconToggle>file_copy</IconToggle>
              <IconToggle>delete</IconToggle>
              */}
            </Card.ActionIcons>
          </Card.Actions>
        </div>
      );
    }
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
            <div className="mdc-typography--caption">
              #{this.props.question.pk} {this.props.gettext("by")}{" "}
              {this.props.question.user.username}
            </div>
          </div>
          {this.cardBody()}
        </Card>
      </div>
    );
  }
}

const getItemStyle = (isDragging, draggableStyle) => ({
  userSelect: "none",
  ...draggableStyle,
});

const getListStyle = (isDraggingOver) => ({
  background: isDraggingOver ? "var(--mdc-theme-primary)" : "lightgrey",
  padding: "10px 10px 1px",
});

export class AssignmentUpdateApp extends Component {
  state = {
    minimizeCards: true,
    showChoices: sessionStorage.answers == "block",
    showImages: sessionStorage.images == "block",
    questions: [],
  };

  handleChoiceToggleClick = () => {
    this.setState({ showChoices: !this.state.showChoices }, () => {
      sessionStorage.answers = this.state.showChoices ? "block" : "none";
    });
  };

  handleImageToggleClick = () => {
    this.setState({ showImages: !this.state.showImages }, () => {
      sessionStorage.images = this.state.showImages ? "block" : "none";
    });
  };

  handleMinimizeToggleClick = () => {
    this.setState({ minimizeCards: !this.state.minimizeCards }, () => {
      sessionStorage.minimizeCards = this.state.minimizeCards
        ? "true"
        : "false";
    });
  };

  refreshFromDB = () => {
    const _this = this;
    const _questions = get(this.props.assignmentURL);
    _questions
      .then((data) => {
        _this.setState({
          questions: data["questions"],
        });
      })
      .catch((error) => console.error(error));
  };

  componentDidMount() {
    this.refreshFromDB();
  }

  onDragEnd = () => {
    console.log("Drag end");
    // the only one that is required
  };

  render() {
    if (this.state.minimizeCards) {
      return (
        <div>
          <ToggleVisibleItems
            gettext={this.props.gettext}
            showChoices={this.state.showChoices}
            showImages={this.state.showImages}
            minimizeCards={this.state.minimizeCards}
            handleChoiceToggleClick={this.handleChoiceToggleClick}
            handleImageToggleClick={this.handleImageToggleClick}
            handleMinimizeToggleClick={this.handleMinimizeToggleClick}
          />
          <DragDropContext nonce={this.props.nonce} onDragEnd={this.onDragEnd}>
            <Droppable droppableId="questions">
              {(provided, snapshot) => (
                <div
                  {...provided.droppableProps}
                  ref={provided.innerRef}
                  style={getListStyle(snapshot.isDraggingOver)}
                >
                  {this.state.questions.map((q, index) => (
                    <Draggable
                      key={`key-${q.question.pk}`}
                      draggableId={`id-${q.question.pk}`}
                      index={index}
                    >
                      {(provided, snapshot) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                          style={getItemStyle(
                            snapshot.isDragging,
                            provided.draggableProps.style,
                          )}
                        >
                          <QuestionCard
                            question={q.question}
                            gettext={this.props.gettext}
                            showChoices={this.state.showChoices}
                            showImages={this.state.showImages}
                            minimizeCards={this.state.minimizeCards}
                          />
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </DragDropContext>
        </div>
      );
    }
    return (
      <div>
        <ToggleVisibleItems
          gettext={this.props.gettext}
          showChoices={this.state.showChoices}
          showImages={this.state.showImages}
          minimizeCards={this.state.minimizeCards}
          handleChoiceToggleClick={this.handleChoiceToggleClick}
          handleImageToggleClick={this.handleImageToggleClick}
          handleMinimizeToggleClick={this.handleMinimizeToggleClick}
        />
        {this.state.questions.map((q) => (
          <QuestionCard
            question={q.question}
            gettext={this.props.gettext}
            showChoices={this.state.showChoices}
            showImages={this.state.showImages}
            minimizeCards={this.state.minimizeCards}
          />
        ))}
      </div>
    );
  }
}
