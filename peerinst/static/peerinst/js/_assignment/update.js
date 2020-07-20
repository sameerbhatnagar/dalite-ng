//import "preact/debug";
import { Component, createContext, Fragment, h, render } from "preact";
import { DragDropContext, Draggable, Droppable } from "react-beautiful-dnd";
import Card from "preact-material-components/Card";
import Checkbox from "preact-material-components/Checkbox";
import Formfield from "preact-material-components/FormField";
import Snackbar from "preact-material-components/Snackbar";
import IconButton from "preact-material-components/IconButton";

import "preact-material-components/Card/style.css";
import "preact-material-components/Checkbox/style.css";
import "preact-material-components/Snackbar/style.css";
import "preact-material-components/IconButton/style.css";

export { h, render };

const User = createContext();

function getCsrfToken() {
  return document.querySelectorAll("input[name=csrfmiddlewaretoken]")[0].value;
}

async function handleResponse(response) {
  if (response.status == 200 || response.status == 201) {
    return await response.json();
  }

  if (response.status == 401) {
    const data = await response.json();
    const base = new URL(window.location.protocol + window.location.host);
    const url = new URL(data["login_url"], base);
    url.search = `?next=${window.location.pathname}`;
    console.debug(url);
    window.location.href = url;
  }

  if ([400, 403, 404, 405].includes(response.status)) {
    console.info(response);
    throw new Error(response);
  }
}

async function submitData(url, data, method) {
  const response = await fetch(url, {
    method,
    mode: "same-origin",
    cache: "no-cache",
    credentials: "same-origin",
    redirect: "follow",
    referrer: "client",
    headers: new Headers({
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    }),
    body: JSON.stringify(data),
  });
  return await handleResponse(response);
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
    if (this.props.question.category.length > 0) {
      return this.props.question.category.map((el, index) =>
        index > 0 ? `, ${el.title}` : el.title,
      );
    }
    return this.props.gettext("Uncategorized");
  };

  editOrCopy = () => {
    return (
      <User.Consumer>
        {(user) => {
          let mode;
          let title;
          if (
            this.props.question.user
              ? this.props.question.user.username == user
              : false
          ) {
            mode = "edit";
            title = this.props.gettext("Edit");
          } else {
            mode = "file_copy";
            title = this.props.gettext("Copy and edit");
          }
          return (
            <IconButton
              className="mdc-theme--primary"
              style={{ fontFamily: "Material Icons" }}
              title={title}
            >
              {mode}
            </IconButton>
          );
        }}
      </User.Consumer>
    );
  };

  colours = {
    easy: "rgb(30, 142, 62)",
    hard: "rgb(237, 69, 40)",
    tricky: "rgb(237, 170, 30)",
    peer: "rgb(25, 118, 188)",
  };

  getDifficultyLabel = () => {
    return Object.entries(this.props.question.matrix).sort(
      (a, b) => b[1] - a[1],
    )[0][0];
  };

  insertActions = () => (
    <Fragment>
      <div
        style={{
          color: this.colours[this.getDifficultyLabel()],
          position: "relative",
        }}
      >
        <IconButton
          style={{
            fontFamily: "Material Icons",
          }}
          title={this.props.gettext(
            "Difficulty level based on past student answers",
          )}
        >
          info
        </IconButton>
        <div
          style={{
            position: "absolute",
            left: "50%",
            width: "inherit",
            transform: "translateX(-50%)",
            fontSize: "x-small",
            marginTop: "-14px",
          }}
        >
          {Array.from(this.getDifficultyLabel()).map((letter, i) =>
            i == 0 ? letter.toUpperCase() : letter.toLowerCase(),
          )}
        </div>
      </div>
      {this.editOrCopy()}
      <IconButton
        className="mdc-theme--primary"
        onClick={() => this.props.handleQuestionDelete(this.props.rank)}
        style={{ fontFamily: "Material Icons" }}
        title={this.props.gettext("Remove question from assignment")}
      >
        delete
      </IconButton>
    </Fragment>
  );

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
                  {this.props.question.discipline
                    ? this.props.question.discipline.title
                    : this.props.gettext("None")}
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
            <Card.ActionIcons>{this.insertActions()}</Card.ActionIcons>
          </Card.Actions>
        </div>
      );
    }
  };

  render() {
    let byline = "";
    if (this.props.question.user) {
      byline = `${this.props.gettext("by")} ${
        this.props.question.user.username
      }`;
    }
    return (
      <Card>
        <div className="card-header">
          <div
            className="mdc-typography--title bold"
            // eslint-disable-next-line
            dangerouslySetInnerHTML={{ __html: this.props.question.title }}
          />
          <div className="mdc-typography--caption">
            #{this.props.question.pk} {byline}
          </div>
        </div>
        {this.cardBody()}
      </Card>
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
    minimizeCards: false,
    showChoices: sessionStorage.answers == "block",
    showImages: sessionStorage.images == "block",
    questions: [],
    title: "",
    current: [],
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
    this.setState({ minimizeCards: !this.state.minimizeCards });
  };

  handleQuestionDelete = (pk) => {
    this.delete(pk);
  };

  refreshFromDB = () => {
    const _this = this;
    const _questions = get(this.props.assignmentURL);
    _questions
      .then((data) => {
        console.debug(data);
        _this.setState({
          current: data["questions"],
          questions: data["questions"],
          title: data["title"],
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

  componentDidMount() {
    this.refreshFromDB();
  }

  delete = async (pk) => {
    try {
      await submitData(this.props.assignmentQuestionURL + pk, {}, "DELETE");
      this.bar.MDComponent.show({
        message: this.props.gettext("Item removed."),
      });
      this.refreshFromDB();
    } catch (error) {
      console.error(error);
      this.bar.MDComponent.show({
        message: this.props.gettext("An error occurred."),
      });
    }
  };

  save = async () => {
    try {
      await submitData(
        this.props.assignmentURL,
        {
          title: this.state.title,
          questions: this.state.questions,
        },
        "PATCH",
      );
      this.bar.MDComponent.show({
        message: this.props.gettext("Changes saved."),
      });
      this.setState({
        current: this.state.questions,
      });
    } catch (error) {
      console.error(error);
      this.bar.MDComponent.show({
        message: this.props.gettext("An error occurred."),
      });
      this.setState({
        questions: this.state.current,
      });
    }
  };

  onDragEnd = (result) => {
    const _questions = Array.from(this.state.questions);
    const [dragged] = _questions.splice(result.source.index, 1);
    _questions.splice(result.destination.index, 0, dragged);
    _questions.forEach((el, i) => {
      el.rank = i;
    });
    this.setState({
      questions: _questions,
    });
    this.save();
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
          <Snackbar
            ref={(bar) => {
              this.bar = bar;
            }}
          />
        </div>
      );
    }
    return (
      <User.Provider value={this.props.user}>
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
            handleQuestionDelete={this.handleQuestionDelete}
            question={q.question}
            rank={q.pk}
            gettext={this.props.gettext}
            showChoices={this.state.showChoices}
            showImages={this.state.showImages}
            minimizeCards={this.state.minimizeCards}
          />
        ))}
        <Snackbar
          ref={(bar) => {
            this.bar = bar;
          }}
        />
      </User.Provider>
    );
  }
}
