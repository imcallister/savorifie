var React = require('react')


module.exports = React.createClass({
    render: function(){
       return <div>
        <div className={'helpText'}>
        	'Expects an ofx or qfx file with headers:';
            <ul>
            	<li className={'helpText'}>Date</li>
            	<li>Something else</li>
            </ul>
            It is currently confgured to expect the headers row to be on row ??.
        </div>
      </div>
   }
})