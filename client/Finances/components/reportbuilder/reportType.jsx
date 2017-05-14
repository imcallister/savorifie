var React = require('react')
var DropdownButton = require('react-bootstrap/lib/DropdownButton');
var MenuItem = require('react-bootstrap/lib/MenuItem');




class ReportType extends React.Component {
  constructor() {
      super();
    }

  render() {

    function renderMenuItem(i) {
      return <MenuItem key={i.key} eventKey={i.key}>{i.label}</MenuItem>
    }

    return (
      <div>
        <h3>Report:
          <DropdownButton id='reportType.dropdown'
                          onSelect={this.props.handleReportTypeSelect}
                          title={this.props.reportLabel || "Choose Report"} >
            {this.props.choices.map(renderMenuItem)}
          </DropdownButton>
        </h3>
      </div>
    )
  }
}

module.exports = ReportType