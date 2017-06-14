var React = require('react');


class InputForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {value: ''};

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(event) {
    this.setState({value: event.target.value});
  }

  handleSubmit(event) {
    this.props.onSubmit(this.state.value);
  }

  render() {
    return (
      <div>
        <form onSubmit={this.handleSubmit.bind(this)}>
          <label>
            {this.props.label}
            <input type="text" value={this.state.value} onChange={this.handleChange} />
          </label>
          <input type="submit" value="Submit" />
        </form>
        <div className={'row'}>
            {this.props.messages.length > 0 ? 
              <div className={'panel panel-default'}>
                <div className={'panel-heading'}>
                    <h3 className={'panel-title'}>Messages</h3>
                </div>
                <div className={'panel-body'}>
                  <ul className={"list-group"}>
                    {
                      this.props.messages.map(function(msg, i) {
                        return <li className={"list-group-item"}>{msg}</li>
                      })
                    }
                  </ul>
                </div>
              </div> 
              : null}
        </div>
      </div>
    );
  }
}

module.exports = InputForm;