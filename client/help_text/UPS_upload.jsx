var React = require('react')

module.exports = React.createClass({
    render: function(){
       return <div>
        <div className={'helpText'}>
        	Expects a csv file with at least following headers:
        	<ul>
            	<li>Account Number</li>
            	<li>Invoice Number</li>
            	<li>Pickup Date</li>
            	<li>Net Amount</li>
            	<li>Tracking Number</li>
            </ul>
            It is currently confgured to expect the headers row to be on row 7.
        </div>
      </div>
   }
})