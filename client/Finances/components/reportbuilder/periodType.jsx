var React                   = require('react')
var Button = require('react-bootstrap/lib/Button');
var ButtonGroup = require('react-bootstrap/lib/ButtonGroup');
var DropdownButton = require('react-bootstrap/lib/DropdownButton');
var MenuItem = require('react-bootstrap/lib/MenuItem');
var Grid = require('react-bootstrap/lib/Grid');
var Col = require('react-bootstrap/lib/Col');
var _ = require('lodash')


function _getLabel(k, choices) {
  if (k) {
    return choices.find(o => o.key === k).label;
  }
  else {
    return "Choose....";
  }
};

function _getByChoices(period) {
  if (period=='year') {
    return _.filter(byChoices, o => _.includes(['month', 'quarter', 'half', 'year'], o.key))
  }
  else if (period=='half') {
    return _.filter(byChoices, o => _.includes(['month', 'quarter', 'half'], o.key))
  }
  else if (period=='quarter') {
    return _.filter(byChoices, o => _.includes(['month', 'quarter'], o.key))
  }
  else if (period=='month') {
    return _.filter(byChoices, o => _.includes(['month'], o.key))
  }
}

var periodChoices = [{key: "year", label: "Year"},
                     {key: "half", label: "Half"},
                     {key: "quarter", label: "Quarter"},
                     {key: "month", label: "Month"}];

var yearChoices = [{key: '2013', label: '2013'},
                   {key: '2014', label: '2014'},
                   {key: '2015', label: '2015'},
                   {key: '2016', label: '2016'},
                   {key: '2017', label: '2017'}];

var monthChoices = [{key: 'M01', label: 'January'},
                    {key: 'M02', label: 'February'},
                    {key: 'M03', label: 'March'},
                    {key: 'M04', label: 'April'},
                    {key: 'M05', label: 'May'},
                    {key: 'M06', label: 'June'},
                    {key: 'M07', label: 'July'},
                    {key: 'M08', label: 'August'},
                    {key: 'M09', label: 'September'},
                    {key: 'M10', label: 'October'},
                    {key: 'M11', label: 'November'},
                    {key: 'M12', label: 'September'}];

var quarterChoices = [{key: '1', label: 'Q1'},
                      {key: '2', label: 'Q2'},
                      {key: '3', label: 'Q3'},
                      {key: '4', label: 'Q4'}];

var halfChoices = [{key: '1', label: 'H1'},
                  {key: '2', label: 'H2'}];

var byChoices = [{'key': 'month', 'label': 'Month'},
                 {'key': 'quarter', 'label': 'Quarter'},
                 {'key': 'half', 'label': 'Half'},
                 {'key': 'year', 'label': 'Year'},
              ]

function renderMenuItem(i) {
    return <MenuItem key={i.key} eventKey={i.key}>{i.label}</MenuItem>
  }


class PeriodType extends React.Component {

  constructor() {
      super();
      this.renderPeriodicity = this.renderPeriodicity.bind(this);
      this.renderMonthlyPeriod = this.renderMonthlyPeriod.bind(this);
      
    }


  renderAsOfQuickLinks() {
    return (
      <div>
        <h3>Quick Links</h3>
        <ButtonGroup vertical>
            <Button bsStyle="primary" id="today" href="#" onClick={() => this.props.handleQuickLinkSelect("today")} >Today</Button>
            <Button bsStyle="primary" id="this_month" href="#" onClick={() => this.props.handleQuickLinkSelect("end_of_last_month")} >End of Last Month</Button>
            <Button bsStyle="primary" id="last_month" href="#" onClick={() => this.props.handleQuickLinkSelect("QTD")} >Quarter-to-date</Button>
            <Button bsStyle="primary" id="trailing_12months" href="#" onClick={() => this.props.handleQuickLinkSelect("YTD")} >Year-to-date</Button>
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
            <Button bsStyle="primary" id="YTD" href="#" onClick={() => this.props.handleQuickLinkSelect("YTD")} >Year-to-date</Button>
            <Button bsStyle="primary" id="QTD" href="#" onClick={() => this.props.handleQuickLinkSelect("QTD")} >Quarter-to-date</Button>
            <Button bsStyle="primary" id="trailing_12months" href="#" onClick={() => this.props.handleQuickLinkSelect("trailing_12months")} >Trailing 12 months</Button>
          </ButtonGroup>
        </div>
      )
  }

  renderQuickLinks() {
    var rptCategory = this.props.choices.find(o => o.key === this.props.reportType).type;
    if (rptCategory=="as_of") {
      return this.renderAsOfQuickLinks();
    }
    else {
      return this.renderDiffQuickLinks();
    }
  }


  renderPeriodicity() {
    return (
      <tr>
        <td><h3>Duration:</h3></td>
        <td>
          <h3>
            <DropdownButton id='periodType.periodicityDropdown' 
                          onSelect={this.props.handlePeriodSelect.bind(this, 'periodType')}
                          title={_getLabel(this.props.periodType, periodChoices)} >
              {periodChoices.map(renderMenuItem)}
            </DropdownButton>
          </h3>
        </td>
      </tr>
    )
  }

  renderYear() {
    if (this.props.periodType) {
      return (
        <tr>
          <td><h3>Year:</h3></td>
          <td><h3>
              <DropdownButton id='periodType.yearDropdown'
                              onSelect={this.props.handlePeriodSelect.bind(this, 'year')}
                              title={_getLabel(this.props.year, yearChoices)} >
                {yearChoices.map(renderMenuItem)}
              </DropdownButton>
            </h3>
          </td>
        </tr>
     )}
  }

  renderMonthlyPeriod() {
    return (
        <tr>
          <td><h3>Month:</h3></td>
          <td><h3><DropdownButton id='periodType.monthDropdown'
                            onSelect={this.props.handlePeriodSelect.bind(this, 'month')}
                            title={_getLabel(this.props.month, monthChoices)} >
              {monthChoices.map(renderMenuItem)}
            </DropdownButton>
          </h3></td>
        </tr>
     ) 
  }

  renderQuarterlyPeriod() {
    return (
      <tr>
        <td><h3>Quarter:</h3></td>
        <td><h3>  <DropdownButton id='periodType.quarterDropdown'
                          onSelect={this.props.handlePeriodSelect.bind(this, 'quarter')}
                          title={_getLabel(this.props.quarter, quarterChoices)} >
            {quarterChoices.map(renderMenuItem)}
          </DropdownButton>
        </h3></td>
      </tr>
     ) 
  }

  renderHalfPeriod() {
    return (
       <tr>
        <td><h3>Half:</h3></td>
        <td><h3>  <DropdownButton id='periodType.halfDropdown'
                          onSelect={this.props.handlePeriodSelect.bind(this, 'half')}
                          title={_getLabel(this.props.half, halfChoices)} >
            {halfChoices.map(renderMenuItem)}
          </DropdownButton>
        </h3></td>
      </tr>
     ) 
  }


  renderBy() {
    var choices =  _getByChoices(this.props.periodType);
    if (this.props.periodType) {
      return (
        <tr>
          <td>
            <h3>
              By:
            </h3>
          </td>
          <td>
            <h3>
              <DropdownButton id='periodType.byDropdown'
                              onSelect={this.props.handlePeriodSelect.bind(this, 'by')} 
                              title={_getLabel(this.props.by, choices)} >
                {choices.map(renderMenuItem)}
              </DropdownButton>
            </h3>
          </td>
        </tr>
       )
    } 
  }
  
  renderPeriod() {
    switch (this.props.periodType) {
      case "half":
        return this.renderHalfPeriod();
      case "quarter":
        return this.renderQuarterlyPeriod();
      case "month":
        return this.renderMonthlyPeriod();
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
                <table>
                  <tbody>
                    {this.renderPeriodicity()}
                    {this.renderYear()}
                    {this.renderPeriod()}
                    {this.renderBy()}
                  </tbody>
                </table>
              </div>
            </div>
          </Col>
        </row>
      </Grid>
    )
  }
}

module.exports = PeriodType
