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
              <i className={"fa fa-refresh fa-spin fa-3x fa-fw"}></i>
              <span class="sr-only">Loading...</span>
            </div>
            <div className={'row'}>
                
            </div>
          </div>
        );
  }
}

module.exports = JobDisplay;