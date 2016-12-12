var React = require('react')
var ReactDOM = require('react-dom')

var BSTable = require('../containers/acctifieTableContainer')


var shipmentcount_cols  = [{'fld': 'order', 'label': 'Shipment'},
			                {'fld': 'BE1', 'label': 'BE1'},
			                {'fld': 'BE2', 'label': 'BE2'},
			                {'fld': 'BE3', 'label': 'BE3'},
			                {'fld': 'SYE1', 'label': 'SYE1'},
			                {'fld': 'SYE2', 'label': 'SYE2'},
			                {'fld': 'SYE3', 'label': 'SYE3'}
			                ]

ReactDOM.render(<BSTable source="/api/inventory/COGS/?raw=true" columns={shipmentcount_cols} />, 
				document.getElementById('cogs.COGS'))

ReactDOM.render(<BSTable source="/api/inventory/shipmentcounts/?raw=true" columns={shipmentcount_cols} />, 
				document.getElementById('cogs.shipmentCounts'))


ReactDOM.render(<BSTable source="/api/accounting/fifo_counts/?raw=true" columns={shipmentcount_cols} />, 
				document.getElementById('cogs.fifoCounts'))


ReactDOM.render(<BSTable source="/api/accounting/fifo_available/?raw=true" columns={shipmentcount_cols} />, 
				document.getElementById('cogs.fifoAvailable'))
