var React = require('react');
var request = require('superagent');
var Cookies = require('js-cookie');

var UploaderCmpnt = require('../components/uploader');  


class UploaderContainer extends React.Component {

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
        this.state.statusMessages.push(err);
      }
      else {
        var rsp = JSON.parse(res.text);
        var msgs = rsp.errors;
        msgs.push(rsp.summary);
        this.setState({statusMessages: msgs});
      }
    }

    onDrop(acceptedFiles) {
      this.setState({
        statusMessages: ['Uploading 1 file']
      });

      var req = request.post(this.props.postUrl);
        
      acceptedFiles.forEach((file)=> {
          req.attach(file.name, file);
      });
      
      req.set('X-CSRFToken', this.state.csrftoken)
         .end(this.updateMessages.bind(this));
    }

    render() {
      return (
          <UploaderCmpnt onDrop={this.onDrop.bind(this)} instructions={this.props.instructions} messages={this.state.statusMessages}></UploaderCmpnt>
      );
    }
}

module.exports = UploaderContainer;
