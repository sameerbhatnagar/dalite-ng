import { Component, createContext, Fragment, h } from "preact";

import Card from "preact-material-components/Card";
import Dialog from "preact-material-components/Dialog";
import IconButton from "preact-material-components/IconButton";

import "preact-material-components/Card/style.css";
import "preact-material-components/IconButton/style.css";

export const User = createContext();

class Image extends Component {
  render() {
    if (this.props.url) {
      return (
        <img
          alt={this.props.altText}
          className="mdc-typography--caption question-image"
          src={this.props.url}
          style={{ display: this.props.show ? "block" : "none" }}
        />
      );
    }
  }
}

const Checkmark = (props) => {
  if (props.correct) {
    return <i className="check material-icons">check</i>;
  }
};

class Choices extends Component {
  choiceList = () => {
    return this.props.choices.map((choice) => {
      return (
        <li className="dense-list">
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

export class QuestionCard extends Component {
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
          let onclick;
          if (
            this.props.question.user
              ? this.props.question.user.username == user ||
                this.props.question.collaborators.includes(user)
              : false
          ) {
            mode = "edit";
            title = this.props.gettext("Edit");
            onclick = () =>
              (window.location = this.props.editURL + this.props.question.pk);
          } else {
            mode = "file_copy";
            title = this.props.gettext("Copy and edit");
            onclick = () =>
              (window.location = this.props.cloneURL + this.props.question.pk);
          }
          return (
            <IconButton
              className="mdc-theme--primary"
              onclick={onclick}
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
          onClick={() => {
            this.dialog.MDComponent.show();
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
              <div className="mdc-typography--caption">
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
      <div>
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
        <Dialog
          ref={(dialog) => {
            this.dialog = dialog;
          }}
        >
          <Dialog.Header>{this.props.question.title}</Dialog.Header>
          <Dialog.Body>Test</Dialog.Body>
          <Dialog.Footer>
            {/*
            <Dialog.FooterButton cancel={true}>Decline</Dialog.FooterButton>
            <Dialog.FooterButton accept={true}>Accept</Dialog.FooterButton>
            */}
          </Dialog.Footer>
        </Dialog>
      </div>
    );
  }
}
