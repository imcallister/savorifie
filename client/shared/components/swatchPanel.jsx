var React = require('react')
var classNames = require('classnames');

import '../../styles/dashboardStyles.scss';

module.exports = React.createClass({
    render: function(){
       return (
            <div className={classNames('dbpanel', this.props.color, 'row', 'no-padding')}>
                <div className={classNames('col-md-5', 'widget-left')}>
                    <svg></svg>
                </div>
                <div className={classNames('col-md-7', 'widget-right')}>
                    <div className={'large'}>{ this.props.bigText }</div>
                    <div className={'text-muted'}>{ this.props.smallText }</div>
                </div>
            </div>
            );
   }
})