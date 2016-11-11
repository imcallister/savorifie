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

var yearChoices = [{key: '2013', label: '2013'},
                   {key: '2014', label: '2014'},
                   {key: '2015', label: '2015'},
                   {key: '2016', label: '2016'},
                   {key: '2017', label: '2017'}];

var monthChoices = [{key: 'jan', label: 'January'},
                   {key: 'feb', label: 'February'},
                   {key: 'mar', label: 'March'},
                   {key: 'apr', label: 'April'},
                   {key: 'may', label: 'May'}];

var quarterChoices = [{key: 'Q1', label: 'Q1'},
                      {key: 'Q2', label: 'Q2'},
                      {key: 'Q3', label: 'Q3'},
                      {key: 'Q4', label: 'Q4'}];

var halfChoices = [{key: 'H1', label: 'H1'},
                  {key: 'H2', label: 'H2'}];


function renderMenuItem(i) {
    return <MenuItem key={i.key} eventKey={i.key}>{i.label}</MenuItem>
  }


class PeriodType extends React.Component {

  constructor() {
      super();
      this.yearSelect = this.yearSelect.bind(this);
      this.monthSelect = this.monthSelect.bind(this);
      this.quarterSelect = this.quarterSelect.bind(this);
      this.halfSelect = this.halfSelect.bind(this);

      this.periodicitySelect = this.periodicitySelect.bind(this);
      this.renderPeriodicity = this.renderPeriodicity.bind(this);
      this.renderMonthlyPeriod = this.renderMonthlyPeriod.bind(this);
      this.state = {periodType: 'Choose Period', quickLink: null, periodicity: null, year: null, quarter: null, month: null, half: null};
    }


  renderAsOfQuickLinks() {
    return (
      <div>
        <h3>Quick Links</h3>
        <ButtonGroup vertical>
            <Button bsStyle="primary" id="today" href="#" onClick={() => this.props.handleQuickLinkSelect("today")} >Month-to-date</Button>
            <Button bsStyle="primary" id="this_month" href="#" onClick={() => this.props.handleQuickLinkSelect("this_month")} >Last Month</Button>
            <Button bsStyle="primary" id="last_month" href="#" onClick={() => this.props.handleQuickLinkSelect("last_month")} >Quarter-to-date</Button>
            <Button bsStyle="primary" id="trailing_12months" href="#" onClick={() => this.props.handleQuickLinkSelect("trailing_12months")} >Trailing 12 months</Button>
        </ButtonGroup>
      </div>
    )
  }

  renderDiffQuickLinks() {
      return (
        <div>
          <h3>Quick Links</h3>
          <ButtonGroup vertical>
            <Button bsStyle="primary" id="MTD" href="#" onClick={() => this.props.handleQuickLinkSelect("MTD")} >Month-to-date</Button>
            <Button bsStyle="primary" id="last_month" href="#" onClick={() => this.props.handleQuickLinkSelect("last_month")} >Last Month</Button>
            <Button bsStyle="primary" id="QTD" href="#" onClick={() => this.props.handleQuickLinkSelect("QTD")} >Quarter-to-date</Button>
            <Button bsStyle="primary" id="trailing_12months" href="#" onClick={() => this.props.handleQuickLinkSelect("trailing_12months")} >Trailing 12 months</Button>
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

  renderPeriodicity() {
    return (
      <h3>Periodicity:
        <DropdownButton id='periodType.periodicityDropdown' onSelect={this.periodicitySelect} title={this.state.periodicity || "Choose..."} >
          {periodChoices.map(renderMenuItem)}
        </DropdownButton>
      </h3>
    )
  }

  renderYear() {
    if (this.state.periodicity) {
      return (
        <h3>Year:
          <DropdownButton id='periodType.yearDropdown' onSelect={this.yearSelect} title={this.state.year || "Choose..."} >
            {yearChoices.map(renderMenuItem)}
          </DropdownButton>
        </h3>
     )}
  }

  renderMonthlyPeriod() {
    return (
        <h3>Month:
          <DropdownButton id='periodType.monthDropdown' onSelect={this.monthSelect} title={this.state.month || "Choose..."} >
            {monthChoices.map(renderMenuItem)}
          </DropdownButton>
        </h3>
     ) 
  }

  renderQuarterlyPeriod() {
    return (
        <h3>Quarter:
          <DropdownButton id='periodType.quarterDropdown' onSelect={this.quarterSelect} title={this.state.quarter || "Choose..."} >
            {quarterChoices.map(renderMenuItem)}
          </DropdownButton>
        </h3>
     ) 
  }

  renderHalfPeriod() {
    return (
        <h3>Half:
          <DropdownButton id='periodType.halfDropdown' onSelect={this.halfSelect} title={this.state.half || "Choose..."} >
            {halfChoices.map(renderMenuItem)}
          </DropdownButton>
        </h3>
     ) 
  }
  
  renderPeriod() {
    if (this.state.year) {
      switch (this.state.periodicity) {
        case "Half":
          return this.renderHalfPeriod();
        case "Quarter":
          return this.renderQuarterlyPeriod();
        case "Month":
          return this.renderMonthlyPeriod();
      }
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
            <div className="panel panel-default">
              <div className="panel-body">
                {this.renderPeriodicity()}
                {this.renderYear()}
                {this.renderPeriod()}
              </div>
            </div>
          </Col>
        </row>
      </Grid>
    )
  }

  periodicitySelect(e) {
    this.props.handlePeriodSelect(e);
    this.setState({ periodicity: periodChoices.find(o => o.key === e).label});
  }

  yearSelect(e) {
    this.props.handlePeriodSelect(e);
    this.setState({ year: e});
  }

  monthSelect(e) {
    this.props.handlePeriodSelect(e);
    this.setState({ month: e});
  }


  halfSelect(e) {
    this.props.handlePeriodSelect(e);
    this.setState({ half: e});
  }


  quarterSelect(e) {
    this.props.handlePeriodSelect(e);
    this.setState({ quarter: e});
  }
}

module.exports = PeriodType

