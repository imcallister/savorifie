var React = require('react')
var DropdownButton = require('react-bootstrap/lib/DropdownButton');
var MenuItem = require('react-bootstrap/lib/MenuItem');



var choices = [{key: 'trialbal', label: 'Trial Balance'},
               {key: 'balsheet', label: 'Balance Sheet'},
               {key: 'incstate', label: 'Income Statement'}

  ];



class ReportType extends React.Component {

  
  constructor() {
      super();
      this.state = {reportType: null, reportLabel: 'Choose report type'};
      this.handleReportTypeSelect = this.handleReportTypeSelect.bind(this);
    }


  handleReportTypeSelect(event) {
    console.log('handleButtonSelect', event);
    this.setState({reportType: event});
    this.setState({reportLabel: choices.find(o => o.key === event).label})
  }

  render() {

    
    function renderMenuItem(i) {
      return <MenuItem eventKey={i.key}>{i.label}</MenuItem>
    }

    return (
      <div>
        <DropdownButton onSelect={this.handleReportTypeSelect} title={this.state.reportLabel} >
          {choices.map(renderMenuItem)}
        </DropdownButton>

        <button className="btn-primary pull-right" onClick={this.props.nextStep}>Save &amp; Continue</button>

      </div>
    )
  }

  nextStep(e) {
    e.preventDefault()
    this.props.saveValues(this.state)
    this.props.nextStep()
  }
}

module.exports = ReportType