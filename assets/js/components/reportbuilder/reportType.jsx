var React = require('react')
var DropdownButton = require('react-bootstrap/lib/DropdownButton');
var MenuItem = require('react-bootstrap/lib/MenuItem');




class ReportType extends React.Component {
  constructor() {
      super();
      this.select = this.select.bind(this);
      if (this.props) {
        this.state = { reportLabel: this.props.fieldValues.reportLabel};
      }
      else {
        this.state = { reportLabel: "Choose report"};
      }
    }

  render() {

    function renderMenuItem(i) {
      return <MenuItem key={i.key} eventKey={i.key}>{i.label}</MenuItem>
    }

    return (
      <div>
        <h3>Report:
          <DropdownButton id='reportType.dropdown' onSelect={this.select} title={this.state.reportLabel} >
            {this.props.choices.map(renderMenuItem)}
          </DropdownButton>
        </h3>
      </div>
    )
  }

  select(e) {
    this.props.handleReportTypeSelect(e);
    this.setState({ reportLabel: this.props.fieldValues.reportLabel});
  }
}

module.exports = ReportType