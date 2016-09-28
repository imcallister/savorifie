var React = require('react')
var ReactDOM = require('react-dom')
var moment = require('moment')
var App = require('./app')
var BHelp = require('./help') 
var CommentBox = require('./tutorial') 
var DataTable = require('./fdatatable')
var BSTable = require('./remote_table')

ReactDOM.render(<BHelp/>, document.getElementById('the-help'));

function priceFormatter(cell, row){
          return '<i class="glyphicon glyphicon-usd"></i> ' + cell;
        };

function dateFormatter(cell, row){
          return moment(cell).format('DD MMM YYYY');
        };

var tbl_columns = [{'fld': 'invoice_number', 'label': 'Invoice #'},
                   {'fld': 'last_date', 'label': 'Last Date', formatter: dateFormatter},
                   {'fld': 'charge', 'label': 'Charge', formatter: priceFormatter}
                   ]

ReactDOM.render(<BSTable source="/api/fulfill/UPS_invoices/?raw=true"
                         columns={tbl_columns} />, document.getElementById('the-help2'));
