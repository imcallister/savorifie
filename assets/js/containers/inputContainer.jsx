var React = require('react');
var request = require('superagent');
var Cookies = require('js-cookie');

var InputCmpnt = require('../components/input');  


class InputContainer extends React.Component {

    constructor() {
      super();
      this.state = { statusMessages: [], csrftoken: Cookies.get('csrftoken')};
    }

    componentDidMount() {

    }

    componentWillUnmount() {
    }

    updateMessages(err, res) {
      if (err) {
        console.log('updateMessages', err);
        this.state.statusMessages.push(err);
      }
      else {
        var rsp = JSON.parse(res.text);
        var msgs = rsp.errors;
        msgs.push(rsp.summary);
        this.setState({statusMessages: msgs});
      }
    }

    onSubmit(value) {
      this.setState({
        statusMessages: ['Fetching order']
      });

      var req = request.post(this.props.postUrl);
        
      
      req.send({'input_value': value})
         .set('X-CSRFToken', this.state.csrftoken)
         .end(this.updateMessages.bind(this));
    }

    render() {
      return (
          <InputCmpnt onSubmit={this.onSubmit.bind(this)} label={this.props.label} messages={this.state.statusMessages}></InputCmpnt>
      );
    }
}

module.exports = InputContainer;
