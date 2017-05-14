var React = require('react');


var ReportBuilderCmpnt = require('../components/reportbuilder/component');

var request = require('superagent');

var assign  = require('object-assign')

var quicklinks = {'today': 'date=today',
                  'end_of_last_month': 'date=end_of_last_month',
                  'MTD': 'col_tag=current_MTD',
                  'QTD': 'col_tag=current_QTD',
                  'YTD': 'col_tag=current_YTD',
                  'trailing_12months': 'col_tag=12Mtrailing'}



class ReportBuilder extends React.Component {

    constructor() {
      super();
      this.state = {step: 1,
                    showModal: false,
                    reports: [],
                    reportType  : null,
                    reportLabel : null,
                    periodType  : null,
                    quickLink   : null,
                    by          : null,
                    year        : null,
                    half        : null,
                    quarter     : null,
                    month       : null
                  };

      this.open = this.open.bind(this);
      this.close = this.close.bind(this);
      
      this.handleReportTypeSelect = this.handleReportTypeSelect.bind(this);
      this.handlePeriodSelect = this.handlePeriodSelect.bind(this);
      this.handleQuickLinkSelect = this.handleQuickLinkSelect.bind(this);
      this.generateReport = this.generateReport.bind(this);
      this.setReports = this.setReports.bind(this);
      this.goBack = this.goBack.bind(this);

      
    }

    componentDidMount() {
      request
        .get('/api/reporting/reportdef/?raw=true')
        .end(this.setReports);
    }

    setReports(err, res) {
      this.setState({'reports': JSON.parse(res.text)
                                    .map((x) => ({key: x.name, label: x.description, type: x.calc_type}))});
    }

    close() {
      this.setState({ showModal: false });
    }

    open() {
      this.setState({ showModal: true });
    }

    handleReportTypeSelect(event) {
      this.setState({reportType: event});
      this.setState({reportLabel: this.state.reports.find(o => o.key === event).label});
      this.setState({'step': 2});
    }

    handlePeriodSelect(fld, event) {
      this.setState({[fld]: event});
    }

    handleQuickLinkSelect(event) {
      this.setState({quickLink: event}, this.generateReport);
    }

    goBack() {
      this.setState({step: 1});
    }

    reportString() {
      // validate
      if (this.state.periodType=='year') {
        if (this.state.year && this.state.by) {
          return "/?period=year&year=" + this.state.year + "&by=" + this.state.by;
        }
      }
      else if (this.state.periodType=='half') {
        if (this.state.year && this.state.half && this.state.by) {
          return "/?period=half&year=" + this.state.year + '&half=' + this.state.half + "&by=" + this.state.by;
        }
      }
      else if (this.state.periodType=='quarter') {
        if (this.state.year && this.state.quarter && this.state.by) {
          return "/?period=quarter&year=" + this.state.year + '&quarter=' + this.state.quarter + "&by=" + this.state.by;
        }
      }
      else if (this.state.periodType=='month') {
        if (this.state.year && this.state.month && this.state.by) {
          return "/?period=month&year=" + this.state.year + '&month=' + this.state.month + "&by=" + this.state.by;
        }
      }
      // generate string
    }

    callReport(rpt, rptString) {
      window.location = '/reporting/reports/' + rpt + '/?' + rptString;
    }


    
    generateReport() {
      this.setState({step: 3}, function() {
        if (this.state.quickLink) {
          window.location = '/reporting/reports/' + this.state.reportType + '/?' + quicklinks[this.state.quickLink];        
        }
        else {
          window.location = '/reporting/reports/' + this.state.reportType + this.reportString();
        }  
      });
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
                              goBack={this.goBack}
                              generateReport={this.generateReport}
                              reportType={this.state.reportType}
                              reportLabel={this.state.reportLabel}
                              periodType={this.state.periodType}
                              quickLink={this.state.quickLink}
                              year={this.state.year}
                              half={this.state.half}
                              quarter={this.state.quarter}
                              month={this.state.month}
                              by={this.state.by}
                              fieldValues={this.state}
                              handleReportTypeSelect={this.handleReportTypeSelect} 
                              handlePeriodSelect={this.handlePeriodSelect}
                              handleBySelect={this.handleBySelect}
                              handleQuickLinkSelect={this.handleQuickLinkSelect} 
                              choices={this.state.reports} />
        </div>
        )
    }
}

module.exports = ReportBuilder;
