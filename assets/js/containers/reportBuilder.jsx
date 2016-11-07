var React = require('react');

var ReportType = require('../components/reportbuilder/reportType')
var PeriodType = require('../components/reportbuilder/timePeriodType')

var assign  = require('object-assign')


var fieldValues = { reportType     : null,
                    age      : null,
                    colors   : []
                  }



class ReportBuilder extends React.Component {

    constructor() {
      super();
      this.state = {step: 1};
    }

    saveValues(field_value) {
      return function() {
        fieldValues = assign({}, fieldValues, field_value)
      }.bind(this)()
    }

    nextStep() {
      console.log('nextStep', this)
      this.setState({
        step : this.state.step + 1
      })
    }

    previousStep() {
      this.setState({
        step : this.state.step - 1
      })
    }

    showStep() {
      switch (this.state.step) {
        case 1:
          return <ReportType fieldValues={fieldValues}
                             nextStep={this.nextStep.bind(this)}
                             previousStep={this.previousStep}
                             saveValues={this.saveValues} />
        case 2:
          return <PeriodType fieldValues={fieldValues}
                               nextStep={this.nextStep}
                               previousStep={this.previousStep}
                               saveValues={this.saveValues} />
      }
    }

    render() {
      
      var style = {
        width : (this.state.step / 4 * 100) + '%'
      }

      return (
        <main>
          <span className="progress-step">Step {this.state.step}</span>
          <progress className="progress" style={style}></progress>
          {this.showStep()}
        </main>
      )
    }
}

module.exports = ReportBuilder;
