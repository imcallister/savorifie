var React = require('react');


var ReportBuilderCmpnt = require('../components/reportbuilder/component');

var request = require('superagent');

var assign  = require('object-assign')



import '../../stylesheets/baseStyles.less';


var choices = [{key: 'TrialBalance', label: 'Trial Balance', type: 'as_of'},
               {key: 'IncBalanceSheet', label: 'Balance Sheet', type: 'as_of'},
               {key: 'IncomeStatement', label: 'Income Statement', type: 'diff'}

  ];


class ReportBuilder extends React.Component {

    constructor() {
      super();
      this.state = {step: 1,
                    showModal: false};
      this.open = this.open.bind(this);
      this.close = this.close.bind(this);
      this.fieldValues = { reportType  : null,
                           reportLabel : null,
                           periodType  : null,
                           quickLink   : null
                        }

      this.handleReportTypeSelect = this.handleReportTypeSelect.bind(this);
      this.handlePeriodSelect = this.handlePeriodSelect.bind(this);
      this.handleQuickLinkSelect = this.handleQuickLinkSelect.bind(this);
      this.nextStep = this.nextStep.bind(this);
      this.previousStep = this.previousStep.bind(this);
    }

    close() {
      this.setState({ showModal: false });
    }

    open() {
      this.setState({ showModal: true });
    }

    handleReportTypeSelect(event) {
      this.fieldValues.reportType = event;
      this.fieldValues.reportLabel = choices.find(o => o.key === event).label;
      this.setState({step: 2});
    }

    handlePeriodSelect(event) {
      this.fieldValues.periodType = event;
      this.fieldValues.quickLink = false;
    }

    handleQuickLinkSelect(event) {
      console.log('handleQuickLinkSelect', event);
      this.fieldValues.periodType = event;
      this.fieldValues.quickLink = true;
    }

    saveValues(field_value) {
      return function() {
        fieldValues = assign({}, fieldValues, field_value)
      }.bind(this)()
    }

    nextStep() {
      if (this.fieldValues.quickLink) {
        this.setState({
          step : 4
        })
      }
      else {
        this.setState({
          step : this.state.step + 1
        })
      }
    }

    previousStep() {
      this.setState({
        step : this.state.step - 1
      })
    }

    generateReport() {
      this.state.loadingReport = true;
      window.location = '/reporting/reports/' + this.fieldValues.reportType + '/?col_tag=2016Annual';
    }

    isActiveState (state) {
      if (state==this.state.step) {
        return "active"
      }
      else {
        return ""
      }
    }

    
    render() { 
      return (
        <div>
          <ReportBuilderCmpnt step={this.state.step}
                              previousStep={this.previousStep}
                              nextStep={this.nextStep}
                              fieldValues={this.fieldValues}
                              saveValues={this.saveValues} 
                              handleReportTypeSelect={this.handleReportTypeSelect} 
                              handlePeriodSelect={this.handlePeriodSelect}
                              handleQuickLinkSelect={this.handleQuickLinkSelect} 
                              choices={choices} />
        </div>
        )
    }
}

module.exports = ReportBuilder;
