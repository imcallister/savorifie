var React = require('react');
var classNames = require('classnames');

class modalCmpnt extends React.Component {
  constructor() {
    super();
  }

  
  render() {
    return (
      
    <div className={classNames('modal', 'fade', {'modal-wide': this.props.wide})} id={this.props.modalId}>
      <div className={'modal-dialog'} role="document">
        <div className={'modal-content'}>
          <div className={'modal-header'}>
            <button type="button" className={'close'} data-dismiss="modal" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
            <h3>{this.props.modalTitle}</h3>
          </div>
          <div className={'modal-body'}>
            {this.props.content}
          </div>
        </div>
      </div>
    </div>
    );
  }
}

module.exports = modalCmpnt;