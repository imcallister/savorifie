var React                   = require('react')
var getRadioOrCheckboxValue = require('../../lib/radiobox-value')
var Button = require('react-bootstrap/lib/Button');
var ButtonGroup = require('react-bootstrap/lib/ButtonGroup');

class PeriodType extends React.Component {

  constructor() {
      super();
      this.state = {periodType: null, quickLink: null};
      this.handleQuickLinks = this.handleQuickLinks.bind(this);
      this.handlePeriod = this.handlePeriod.bind(this);
      this.nextStep = this.nextStep.bind(this);
    }

  handleQuickLinks(event) {
    this.setState({'periodType': event.target.id, quickLink: true});
  }

  handlePeriod(event) {
    this.setState({'periodType': event.target.id});
  }

  render() {
    return (
      <div>
        <h2>Time Period</h2>
        <h3>Quick Links</h3>
          <ButtonGroup justified onClick={this.handleQuickLinks} >
            <Button id="this_month" href="#">This Month</Button>
            <Button id="last_month" href="#">Last Month</Button>
            <Button id="trailing_12months" href="#">Trailing 12 months</Button>
          </ButtonGroup>

        <h3>Build It -- Period</h3>
          <ButtonGroup justified onClick={this.handlePeriod} >
            <Button id="year" href="#">Year</Button>
            <Button id="half" href="#">Half</Button>
            <Button id="quarter" href="#">Quarter</Button>
            <Button id="month" href="#">Month</Button>
          </ButtonGroup>

            <button className="btn -default pull-left" onClick={this.props.previousStep}>Back</button>
            <button className="btn -primary pull-right" onClick={this.nextStep}>Save &amp; Continue</button>

      </div>
    )
  }

  nextStep() {
    this.props.saveValues(this.state)
    this.props.nextStep()
  }
}

module.exports = PeriodType

