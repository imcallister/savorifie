var React                   = require('react')
var getRadioOrCheckboxValue = require('../../lib/radiobox-value')
var Button = require('react-bootstrap/lib/Button');
var ButtonGroup = require('react-bootstrap/lib/ButtonGroup');

class PeriodBuilder extends React.Component {

  constructor() {
      super();
      this.state = {periodType: null, quickLink: null};
    }


  renderYearBuilder() {
    return (
      <div>
        <h3>Year</h3>
        <ButtonGroup justified onClick={this.props.handleQuickLinkSelect} >
          <Button id="today" href="#">Today</Button>
          <Button id="this_month" href="#">End of Last Month</Button>
          <Button id="last_month" href="#">End of Last Quarter</Button>
          <Button id="trailing_12months" href="#">Trailing 12 months</Button>
        </ButtonGroup>
      </div>
    )
  }

  renderHalfBuilder() {
      return (
        <div>
          <h3>Half Year</h3>
          <ButtonGroup justified onClick={this.props.handleQuickLinkSelect} >
            <Button id="today" href="#">Month-to-date</Button>
            <Button id="this_month" href="#">Last Month</Button>
            <Button id="last_month" href="#">Quarter-to-date</Button>
            <Button id="trailing_12months" href="#">Trailing 12 months</Button>
          </ButtonGroup>
        </div>
      )
  }

  renderQuarterBuilder() {
      return (
        <div>
          <h3>Quarter</h3>
          <ButtonGroup justified onClick={this.props.handleQuickLinkSelect} >
            <Button id="today" href="#">Month-to-date</Button>
            <Button id="this_month" href="#">Last Month</Button>
            <Button id="last_month" href="#">Quarter-to-date</Button>
            <Button id="trailing_12months" href="#">Trailing 12 months</Button>
          </ButtonGroup>
        </div>
      )
  }

  renderMonthBuilder() {
      return (
        <div>
          <h3>Month</h3>
          <ButtonGroup justified onClick={this.props.handleQuickLinkSelect} >
            <Button id="today" href="#">Month-to-date</Button>
            <Button id="this_month" href="#">Last Month</Button>
            <Button id="last_month" href="#">Quarter-to-date</Button>
            <Button id="trailing_12months" href="#">Trailing 12 months</Button>
          </ButtonGroup>
        </div>
      )
  }

  renderPeriodBuilder() {
    switch (this.props.fieldValues.periodType) {
        case "year":
          return renderYearBuilder();
        case "half":
          return renderHalfBuilder();
        case "quarter":
          return renderQuarterBuilder();
        case "month":
          return renderMonthBuilder();
    }
  }
  
  render() {
    return (
      <div>
        <h3>Specify Period</h3>
        {this.renderPeriodBuilder()}
      </div>
    )
  }
}

module.exports = PeriodBuilder

