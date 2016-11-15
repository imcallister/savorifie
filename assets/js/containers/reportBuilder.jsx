var React = require('react');


var ReportBuilderCmpnt = require('../components/reportbuilder/component');

var request = require('superagent');

var assign  = require('object-assign')



import '../../stylesheets/baseStyles.less';


class ReportBuilder extends React.Component {

    constructor() {
      super();
      this.state = {step: 1,
                    showModal: false,
                    reports: []};

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
      this.setReports = this.setReports.bind(this);

      
    }

    componentDidMount() {
      request
        .get('/api/reporting/reportdef/?raw=true')
        .end(this.setReports);
    }

    setReports(err, res) {
      this.setState({'reports': JSON.parse(res.text)
                                    .map((x) => ({key: x.name, label: x.description, type: 'as_of'}))});
    }

    close() {
      this.setState({ showModal: false });
    }

    open() {
      this.setState({ showModal: true });
    }

    handleReportTypeSelect(event) {
      this.fieldValues.reportType = event;
      this.fieldValues.reportLabel = this.state.reports.find(o => o.key === event).label;
      this.setState({step: 2});
    }

    handlePeriodSelect(event) {
      this.fieldValues.periodType = event;
      this.fieldValues.quickLink = false;
    }

    handleQuickLinkSelect(event) {
      console.log('handleQuickLinkSelect', event);
      this.generateReport(event);
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

    generateReport(colTag) {
      this.setState({step: 3});
      this.state.loadingReport = true;
      console.log(this);
      window.location = '/reporting/reports/' + this.fieldValues.reportType + '/?date=' + colTag;
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
                              choices={this.state.reports} />
        </div>
        )
    }
}

module.exports = ReportBuilder;
