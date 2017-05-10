import React, {Component} from 'react';
import Dropzone from 'react-dropzone';

import {Card, CardActions, CardHeader, CardMedia, CardTitle, CardText} from 'material-ui/Card';


var styles = {
    centerFlex: {
      'alignItems': 'center',
      'display': 'flex',
      'justifyContent': 'center'
    },
    'dropZone': {
    borderWidth: '2px',
    borderColor: 'black',
    borderStyle: 'dashed',
    borderRadius: '4px',
    margin: '30px',
    padding: '30px',
    width: '200px',
    transition: 'all 0.5s'
    }
  }

export default class Uploader extends Component {

  constructor() {
    super();
  }
  
  
  render() {
      var msgStyle = {
        textAlign: "left"
      };

        return (
            <div>
                    <div className={'col-md-6'}>
                        <div className={'panel panel-default'}>
                            <div className={'panel-body'}>
                                <div style={styles.centerFlex}>
                                    <Dropzone style={styles.dropZone} ref={(node) => { this.dropzone = node; }} onDrop={this.props.onDrop}>
                                        <h3>
                                          Drag files here or click to get finder window
                                        </h3>
                                    </Dropzone>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className={'col-md-6'}>
                        <Card>
                          <CardTitle title="Upload Instructions" />
                          <CardText>
                            {this.props.instructions}
                          </CardText>
                        </Card>
                        <Card>
                            <CardTitle title="Upload Messages" />
                            
                                  <ul className={"list-group"}>
                                    {
                                      this.props.messages.map(function(msg, i) {
                                        return <li className={"list-group-item"} style={msgStyle}>{msg}</li>
                                      })
                                    }
                                  </ul>
                        </Card>
                    </div>
            </div>
    );
  }
}