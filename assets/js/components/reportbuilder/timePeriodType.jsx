var React                   = require('react')
var getRadioOrCheckboxValue = require('../../lib/radiobox-value')
var Button = require('react-bootstrap/lib/Button');
var ButtonGroup = require('react-bootstrap/lib/ButtonGroup');
var DropdownButton = require('react-bootstrap/lib/DropdownButton');
var MenuItem = require('react-bootstrap/lib/MenuItem');
var Grid = require('react-bootstrap/lib/Grid');
var Col = require('react-bootstrap/lib/Col');


var periodChoices = [{key: "year", label: "Year"},
                     {key: "half", label: "Half"},
                     {key: "quarter", label: "Quarter"},
                     {key: "month", label: "Month"}];

function renderMenuItem(i) {
    return <MenuItem key={i.key} eventKey={i.key}>{i.label}</MenuItem>
  }


class PeriodType extends React.Component {

  constructor() {
      super();
      this.select = this.select.bind(this);
      this.state = {periodType: 'Choose Period', quickLink: null};
    }


  renderAsOfQuickLinks() {
    return (
      <div>
        <h3>Quick Links</h3>
        <ButtonGroup vertical onClick={this.props.handleQuickLinkSelect} >
          <Button bsStyle="primary" id="today" href="#">Today</Button>
          <Button bsStyle="primary" id="this_month" href="#">End of Last Month</Button>
          <Button bsStyle="primary" id="last_month" href="#">End of Last Quarter</Button>
          <Button bsStyle="primary" id="trailing_12months" href="#">Trailing 12 months</Button>
        </ButtonGroup>
      </div>
    )
  }

  renderDiffQuickLinks() {
      return (
        <div>
          <h3>Quick Links</h3>
          <ButtonGroup vertical onClick={this.props.handleQuickLinkSelect} >
            <Button bsStyle="primary" id="today" href="#">Month-to-date</Button>
            <Button bsStyle="primary" id="this_month" href="#">Last Month</Button>
            <Button bsStyle="primary" id="last_month" href="#">Quarter-to-date</Button>
            <Button bsStyle="primary" id="trailing_12months" href="#">Trailing 12 months</Button>
          </ButtonGroup>
        </div>
      )
  }

  
  renderQuickLinks() {
    var rptCategory = this.props.choices.find(o => o.key === this.props.fieldValues.reportType).type;
    if (rptCategory=="as_of") {
      return this.renderAsOfQuickLinks();
    }
    else {
      return this.renderDiffQuickLinks();
    }
  }
  
  render() {
    return (
      <Grid>
        <row>
          <Col md={3}>
            {this.renderQuickLinks()}
          </Col>

          <Col md={3}>
            <h3> Build It</h3>
            <h3>Period:
              <DropdownButton id='periodType.dropdown' onSelect={this.select} title={this.state.periodType} >
                {periodChoices.map(renderMenuItem)}
              </DropdownButton>
            </h3>
          </Col>
        </row>
      </Grid>
    )
  }

  select(e) {
    this.props.handlePeriodSelect(e);
    this.setState({ periodType: periodChoices.find(o => o.key === e).label});
  }
}

module.exports = PeriodType

