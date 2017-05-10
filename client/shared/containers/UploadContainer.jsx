import React, {Component} from 'react';
import request from 'superagent';
import Cookies from 'js-cookie';

import UploaderCmpnt from '../components/uploader';  

export default class UploaderContainer extends Component {

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
          <UploaderCmpnt key={this.props.lbl}
                         onDrop={this.onDrop.bind(this)}
                         instructions={this.props.instructions}
                         messages={this.state.statusMessages}>
          </UploaderCmpnt>
      );
    }
}
