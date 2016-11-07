var React                   = require('react')
var getRadioOrCheckboxValue = require('../../lib/radiobox-value')
var Button = require('react-bootstrap/lib/Button');
var ButtonGroup = require('react-bootstrap/lib/ButtonGroup');

class PeriodType extends React.Component {


  renderOptions(type, name, value, index) {
    var isChecked = function() {
      if (type == 'radio') return value == this.props.fieldValues[name]

      if (type == 'checkbox') return this.props.fieldValues[name].indexOf(value) >= 0

      return false
    }.bind(this)

    return (
      <label key={index}>
        <input type={type} name={name} value={value} defaultChecked={isChecked()} /> {value}
      </label>
    )
  }

  render() {
    return (
      <div>
        <h2>Time Period</h2>
        <h3>Quick Links</h3>
          <ButtonGroup justified>
            <Button href="#">This Month</Button>
            <Button href="#">Last Month</Button>
            <Button href="#">Trailing 12 months</Button>
          </ButtonGroup>

        <h3>Build It -- Period</h3>
          <ButtonGroup justified>
            <Button href="#">Year</Button>
            <Button href="#">Half</Button>
            <Button href="#">Quarter</Button>
            <Button href="#">Month</Button>
          </ButtonGroup>

            <button className="btn -default pull-left" onClick={this.props.previousStep}>Back</button>
            <button className="btn -primary pull-right" onClick={this.nextStep}>Save &amp; Continue</button>

      </div>
    )
  }

  nextStep() {
    // Get values via querySelector
    var age    = document.querySelector('input[name="age"]:checked')
    var colors = document.querySelectorAll('input[name="colors"]')

    var data = {
      age    : getRadioOrCheckboxValue(age),
      colors : getRadioOrCheckboxValue(colors)
    }

    this.props.saveValues(data)
    this.props.nextStep()
  }
}

module.exports = PeriodType

