var React = require('react')
var ReactDOM = require('react-dom')

var BHelp = require('../help_text/bookkeeping') 
var BSTable = require('../containers/acctifieTableContainer')
var Uploader = require('../containers/uploaderContainer') 
var formatters = require('../helpers/formatters')
var ModalCmpnt = require('../components/modalCmpnt')


var help = <BHelp/>
var rcvbl_date = document.getElementById('periodend.receivables').getAttribute('date');
console.log(rcvbl_date);
var rcvbl_url = "/api/reports/receivables/?raw=true&as_of=" + rcvbl_date
var paybl_date = document.getElementById('periodend.payables').getAttribute('date');
var paybl_url = "/api/reports/payables/?raw=true&as_of=" + paybl_date
var fut_rcvbl_date = document.getElementById('periodend.futurereceivables').getAttribute('date');
var fut_rcvbl_url = "/api/reports/future_receivables/?raw=true&as_of=" + fut_rcvbl_date

ReactDOM.render(<ModalCmpnt modalId="help" modalTitle="Help" content={help}/>, 
				document.getElementById('periodend.help'))


var receivables_cols  = [{'fld': 'counterparty', 'counterparty': 'Upload Name'},
					 	  {'fld': 'amount', 'label': 'Amount', formatter: formatters.drill}
					 	  ]

var receivables = <BSTable source={rcvbl_url} columns={receivables_cols} />
ReactDOM.render(receivables, document.getElementById('periodend.receivables'))

var payables_cols  = [{'fld': 'counterparty', 'counterparty': 'Upload Name'},
					 	  {'fld': 'amount', 'label': 'Amount', formatter: formatters.drill}
					 	  ]

var payables = <BSTable source={paybl_url} columns={payables_cols} />
ReactDOM.render(payables, document.getElementById('periodend.payables'))

var future_receivables = <BSTable source={fut_rcvbl_url} columns={receivables_cols} />
ReactDOM.render(future_receivables, document.getElementById('periodend.futurereceivables'))
