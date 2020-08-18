import { Component, h } from "preact";

import { Chip, ChipSet } from "@rmwc/chip";
import { TextField, TextFieldIcon } from "@rmwc/textfield";
import { Typography } from "@rmwc/typography";

// Rely on mdc default styles from global use

import { get } from "../_ajax/ajax.js";

export class TeacherInputWithAutocomplete extends Component {
  state = {
    searchResult: "",
    searchTerm: "",
    teachers: this.props.teachers,
  };

  search = async () => {
    if (this.state.searchTerm != "") {
      try {
        const queryString = new URLSearchParams({
          query: this.state.searchTerm,
        });
        const url = `${this.props.searchURL}?${queryString.toString()}`;
        const data = await get(url);
        console.debug(data);
        if (data.length > 0) {
          this.setState({
            searchResult: data[0]["user"]["username"],
          });
        } else {
          this.setState({
            searchResult: "",
          });
        }
      } catch (error) {
        console.error(error);
      }
    } else {
      this.setState({
        searchResult: "",
      });
    }
  };

  render() {
    return (
      <div>
        <TextField
          dense
          outlined
          placeholder="Add teachers to group"
          onInput={(evt) => {
            this.setState({ searchTerm: evt.target.value }, () =>
              this.search(),
            );
          }}
          value={this.state.searchTerm}
          onKeyDown={(evt) => {
            if (evt.key === "Enter") {
              evt.preventDefault();
            }
            if (evt.key === "Tab") {
              this.setState({ searchTerm: this.state.searchResult });
              evt.preventDefault();
            }
          }}
          style={{ position: "relative " }}
          withTrailingIcon={
            <TextFieldIcon
              tabIndex="0"
              icon={
                this.state.searchTerm.length != 0
                  ? this.state.searchTerm == this.state.searchResult
                    ? "check"
                    : "close"
                  : {}
              }
              onClick={() =>
                this.setState({ searchTerm: "", searchResult: "" })
              }
              theme="primary"
            />
          }
        >
          <div
            style={{
              color: "gray",
              opacity: "0.4",
              position: "absolute",
              bottom: "14px",
              left: "12px",
              letterSpacing: ".04em",
            }}
          >
            {this.state.searchResult}
          </div>
        </TextField>
        <ChipSet>
          <Typography use="body2">
            {this.state.teachers.map((teacher, i) => {
              return (
                <Chip id={`chip-${i}`} text={teacher} theme="secondary" />
              );
            })}
          </Typography>
        </ChipSet>
      </div>
    );
  }
}
