var React = require('react')

module.exports = React.createClass({
    render: function(){
       return <div>
        <h3>UPS Upload</h3>
        
        <div>
        	Expects a csv file with at least following headers:
            <ul>
            	<li>Date</li>
            	<li>Amount Debit</li>
            	<li>Amount Credit</li>
            	<li>Description</li>
            	<li>Transaction Number</li>
            </ul>
            It is currently confgured to expect the headers row to be on row 4.
        </div>
      </div>
   }
})