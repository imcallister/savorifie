var React = require('react')
var ReactDOM = require('react-dom')

var BHelp = require('../components/book_help') 
var BSTable = require('../containers/acctifieTableContainer')
var formatters = require('../helpers/formatters')

ReactDOM.render(<BHelp/>, document.getElementById('the-help'));


var tbl_columns = [{'fld': 'invoice_number', 'label': 'Invoice #'},
                   {'fld': 'last_date', 'label': 'Last Date', formatter: formatters.date},
                   {'fld': 'charge', 'label': 'Charge', formatter: formatters.price}
                   ]

ReactDOM.render(<BSTable source="/api/fulfill/UPS_invoices/?raw=true"
                         columns={tbl_columns} />, document.getElementById('the-help2'));
