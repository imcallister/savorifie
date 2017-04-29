var React = require('react');
var Button = require('react-bootstrap/lib/Button');

class JobDisplay extends React.Component {
  constructor() {
    super();
    this.run = this.run.bind(this);
  }
  
  run() {
    this.props.onRun();
  }

  render() {
      var msgStyle = {
        textAlign: "left"
      };
      return (
        <div>
          {this.props.stage == 'not_started' &&
            <div>
              <Button
                  bsStyle="primary"
                  bsSize="large"
                  onClick={this.run}
                >
                  Fetch Orders
              </Button>
            </div>
          }
          {this.props.stage == 'contacting_AMZN' &&
            <div>
                <i className={"fa fa-refresh fa-spin fa-3x fa-fw"}></i>
            </div> 
          }
          {this.props.stage == 'load_done' &&
              <div>
                <div>
                  <Button
                      bsStyle="primary"
                      bsSize="large"
                      onClick={this.props.OnRun}
                    >
                      Fetch Amazon Orders
                  </Button>
                </div>
                <div className={'panel-body'}>
                  <ul className={"list-group"}>
                    {
                      this.props.messages.map(function(msg, i) {
                        return <li className={"list-group-item"} style={msgStyle}>{msg}</li>
                      })
                    }
                  </ul>
                </div>
              </div>
          }
          
        </div>
        );
  }
}

module.exports = JobDisplay;