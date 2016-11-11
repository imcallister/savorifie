var React = require('react')

var ReportType = require('./reportType')
var PeriodType = require('./timePeriodType')
var PeriodBuilder = require('./periodBuilder')

var Popover = require('react-bootstrap/lib/Popover');
var Tooltip = require('react-bootstrap/lib/Tooltip');
var Modal = require('react-bootstrap/lib/Modal');
var OverlayTrigger = require('react-bootstrap/lib/OverlayTrigger');
var Button = require('react-bootstrap/lib/Button');


class ReportBuilderComponent extends React.Component {
  
  constructor() {
      super();
      this.state = {showModal: false};
      this.open = this.open.bind(this);
      this.close = this.close.bind(this);
      this.renderTypeSection = this.renderTypeSection.bind(this);
    }

    close() {
      this.setState({ showModal: false });
    }

    open() {
      this.setState({ showModal: true });
    }

    isActiveState (state) {
      if (state==this.props.step) {
        return "active"
      }
      else {
        return ""
      }
    }

    renderTitle() {
      return (
          <div className="progress-breadcrumb">
            <span className={this.isActiveState(1)}>Choose Report</span>
            <span className={this.isActiveState(2)}>Choose Period</span>
            <span className={this.isActiveState(3)}>Generating</span>
          </div>
      )
    }

    renderTypeSection() {
    	if (this.props.step==1) {
	      return (
	      	      	<div>
	      		      	<ReportType key="reportType"
	      	      					fieldValues={this.props.fieldValues}
	      	                        nextStep={this.props.nextStep}
	      	                        previousStep={this.props.previousStep}
	      	                        saveValues={this.props.saveValues} 
	                           		handleReportTypeSelect={this.props.handleReportTypeSelect}
	                           		choices={this.props.choices}/>
	      	        </div>
	      	        )
    	} else {
    		return (<h3>Report: {this.props.fieldValues.reportLabel}</h3>)
    	}
	}

	renderFooter() {
    	if (this.props.step!=1) {
	      return (
	      	      	<div>
	      		      	<Button className="btn -primary pull-left" onClick={this.props.previousStep}>Back</Button>
              			<Button className="btn -primary pull-right" onClick={this.props.nextStep}>Next</Button>
	      	        </div>
	      	        )
    	} else {
    		return (<div></div>)
    	}
	}

	renderPeriodSection() {
		if (this.props.step==2) {
      return (
      	<div>
	      	<PeriodType fieldValues={this.props.fieldValues}
                     		nextStep={this.props.nextStep}
                     		previousStep={this.props.previousStep}
                     		handlePeriodSelect={this.props.handlePeriodSelect}
                     		handleQuickLinkSelect={this.props.handleQuickLinkSelect} 
                     		saveValues={this.props.saveValues}
                     		choices={this.props.choices} />
        </div>
      )
		} else if (this.props.step==3) {
  		return (
      	<div>
	      	<PeriodBuilder fieldValues={this.props.fieldValues}
                     		nextStep={this.props.nextStep}
                     		previousStep={this.props.previousStep}
                     		handlePeriodSelect={this.props.handlePeriodSelect}
                     		handleQuickLinkSelect={this.props.handleQuickLinkSelect} 
                     		saveValues={this.props.saveValues}
                     		choices={this.props.choices} />
        </div>
      )
  	}
		else if (this.props.step==4) {
  		window.location = '/reporting/reports/' + this.props.fieldValues.reportType + '/?col_tag=2016Annual';
    	return <h2>LOADING REPORT</h2>
  	} 
    	else {
    		return (<div></div>)
    	}
	}

	render() { 
      return (
        <div>
          <Button
            bsStyle="primary"
            bsSize="large"
            onClick={this.open}
          >
            Launch Report Builder
          </Button>

          <Modal show={this.state.showModal} onHide={this.close}>
            <Modal.Header closeButton>
              <Modal.Title>Build Report</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              <div>
                <div className="row">
                  <div className="panel panel-default">
                    <div className="panel-body">
                      {this.renderTitle()}
                    </div>
                  </div>
                </div>
                <div className="row">
                  <div className="panel panel-default">
                    <div className="panel-body">
			      		{this.renderTypeSection()}
                    </div>
                  </div>
                </div>
                <div className="row">
                  <div className="panel panel-default">
                    <div className="panel-body">
			      		{this.renderPeriodSection()}
                    </div>
                  </div>
                </div>
                
              </div>
            </Modal.Body>
            <Modal.Footer>
              {this.renderFooter()}
            </Modal.Footer>
          </Modal>
        </div>
      )
    }
}

module.exports = ReportBuilderComponent
