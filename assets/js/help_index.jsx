var React = require('react')
var ReactDOM = require('react-dom')
var App = require('./app')
var BHelp = require('./help') 
var CommentBox = require('./tutorial') 
var DataTable = require('./fdatatable')
var BSTable = require('./remote_table')
var formatters = require('./helpers/formatters')

ReactDOM.render(<BHelp/>, document.getElementById('the-help'));


var tbl_columns = [{'fld': 'invoice_number', 'label': 'Invoice #'},
                   {'fld': 'last_date', 'label': 'Last Date', formatter: formatters.date},
                   {'fld': 'charge', 'label': 'Charge', formatter: formatters.price}
                   ]

ReactDOM.render(<BSTable source="/api/fulfill/UPS_invoices/?raw=true"
                         columns={tbl_columns} />, document.getElementById('the-help2'));
