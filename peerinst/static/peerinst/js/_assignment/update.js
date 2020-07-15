import { Component, h, render } from "preact";
import Card from "preact-material-components/Card";
import "preact-material-components/Card/style.css";
import "preact-material-components/Button/style.css";
import IconToggle from "preact-material-components/IconToggle";

export { h, render };

class CardsPage extends Component {
  render() {
    return (
      <div>
        <Card>
          <div className="card-header">
            <h2 className=" mdc-typography--title">Title</h2>
            <div className=" mdc-typography--caption">Caption</div>
          </div>
          <Card.Media className="card-media" />
          <Card.Actions>
            <Card.ActionButtons>
              <Card.ActionButton ripple>OK</Card.ActionButton>
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
  render() {
    return <CardsPage />;
  }
}
