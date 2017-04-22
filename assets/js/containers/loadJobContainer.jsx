var React = require('react');
var request = require('superagent');
var Cookies = require('js-cookie');

var JobDisplayCmpnt = require('../components/loadJob');


class LoadJobContainer extends React.Component {

    constructor() {
      super();
      this.state = { statusMessages: [], csrftoken: Cookies.get('csrftoken')};
    }

    componentDidMount() {
      var req = request.post(this.props.postUrl);
      req.set('X-CSRFToken', this.state.csrftoken)
         .end(this.updateMessages.bind(this));

    }

    componentWillUnmount() {
    }

    updateMessages(err, res) {
      if (err) {
        this.state.statusMessages.push(err);
      }
      else {
        var rsp = JSON.parse(res.text);
        var msgs = rsp.errors;
        msgs.push(rsp.summary);
        this.setState({statusMessages: msgs});
      }
    }

    render() {
      return (
          <JobDisplayCmpnt messages={this.state.statusMessages}></JobDisplayCmpnt>
      );
    }
}

module.exports = LoadJobContainer;
