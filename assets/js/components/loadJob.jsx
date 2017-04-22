var React = require('react');

class JobDisplay extends React.Component {
  constructor() {
    super();
  }
  
  render() {
      var msgStyle = {
        textAlign: "left"
      };
      return (
        <div>
          <div className={'row'}>
            <div className={'col-md-4'}>
            </div>
            <div className={'col-md-4'}>
              <div className={'row'}>
                <i className={"fa fa-refresh fa-spin fa-3x fa-fw"}></i>
              </div>
              <div className={'row'}>
                <span class="sr-only">Loading...</span>
              </div>
            </div>
            <div className={'col-md-4'}>
            </div>
          </div> 
        </div>
        );
  }
}

module.exports = JobDisplay;