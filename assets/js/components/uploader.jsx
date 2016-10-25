var React = require('react');
var Dropzone = require('react-dropzone');

class Uploader extends React.Component {
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
              <div className={'col-md-6'}>
                <div className={'panel panel-default'}>
                  <div className={'panel-body'}>
                    <Dropzone ref={(node) => { this.dropzone = node; }} onDrop={this.props.onDrop}>
                        <div>Try dropping some files here, or click to select files to upload.</div>
                    </Dropzone>
                  </div>
                </div>
              </div>
              <div className={'col-md-6'}>
                <div className={'panel panel-default'}>
                    <div className={'panel-heading'}>
                        <h3 className={'panel-title'}>Instructions</h3>
                    </div>
                    <div className={'panel-body'}>
                      {this.props.instructions}
                    </div>
                </div>
              </div>                
            </div>
            <div className={'row'}>
                {this.props.messages.length > 0 ? 
                  <div className={'panel panel-default'}>
                    <div className={'panel-heading'}>
                        <h3 className={'panel-title'}>Messages</h3>
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
                  : null}
            </div>
          </div>
        );
  }
}

module.exports = Uploader;