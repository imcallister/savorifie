var React = require('react');
var request = require('superagent');
var Cookies = require('js-cookie');

var JobDisplayCmpnt = require('../components/loadJob');


class LoadJobContainer extends React.Component {

    constructor() {
      super();
      this.state = { statusMessages: [], csrftoken: Cookies.get('csrftoken'), stage: 'not_started'};
    }

    componentDidMount() {
    }

    componentWillUnmount() {
    }

    updateMessages(err, res) {
      if (err) {
        this.state.statusMessages.push(err);
      }
      else {
        console.log('LoadJobContainer.updateMessages');
        console.log(res);
        
        var rsp = JSON.parse(res.text);
        var msgs = rsp.errors;
        msgs.push(rsp.summary);
        this.setState({statusMessages: msgs, stage: 'load_done'});
      }
    }

    onRun() {
      this.setState({
        stage: 'contacting_AMZN',
      });

      var req = request.post(this.props.postUrl);
      req.set('X-CSRFToken', this.state.csrftoken)
         .end(this.updateMessages.bind(this));

    }


    render() {
      return (
          <JobDisplayCmpnt messages={this.state.statusMessages}
                           onRun={this.onRun.bind(this)}
                           stage={this.state.stage}>
          </JobDisplayCmpnt>
      );
    }
}

module.exports = LoadJobContainer;
