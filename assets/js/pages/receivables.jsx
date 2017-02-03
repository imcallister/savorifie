var React = require('react')
var ReactDOM = require('react-dom')

var BHelp = require('../help_text/bookkeeping') 
var UPSHelp = require('../help_text/UPS_upload')
var FRBHelp = require('../help_text/FRB_upload')
var BSTable = require('../containers/acctifieTableContainer')
var Uploader = require('../containers/uploaderContainer') 
var formatters = require('../helpers/formatters')
var ModalCmpnt = require('../components/modalCmpnt')


var help = <BHelp/>
var UPS_upload_help = <UPSHelp/>
var FRB_upload_help = <FRBHelp/>

ReactDOM.render(<ModalCmpnt modalId="help" modalTitle="Help" content={help}/>, 
				document.getElementById('bookkeeping.help'))


var receivables_cols  = [{'fld': 'counterparty', 'counterparty': 'Upload Name'},
					 	  {'fld': 'amount', 'label': 'Amount', formatter: formatters.drill}
					 	  ]

var receivables = <BSTable source="/api/reports/receivables/?raw=true" columns={receivables_cols} />
ReactDOM.render(receivables, document.getElementById('bookkeeping.receivables'))


var future_receivables = <BSTable source="/api/reports/future_receivables/?raw=true" columns={receivables_cols} />
ReactDOM.render(future_receivables, document.getElementById('bookkeeping.futurereceivables'))


var unpaid_shopify_cols  = [{'fld': 'label', 'label': 'ID'},
			                {'fld': 'paid_thru', 'label': 'Paid Via'},
			                {'fld': 'sale_date', 'label': 'Date', formatter: formatters.date},
			                {'fld': 'shipping_name', 'label': 'Name'},
			                {'fld': 'proceeds', 'label': 'Proceeds'},
			                {'fld': 'received', 'label': 'Received'},
			                {'fld': 'diff', 'label': 'Difference'},
			                {'fld': 'items_string', 'label': 'SKUs'}
			                ]

var unpaid_shopify = <BSTable source="/api/sales/unpaid_sales/SHOPIFY/?raw=true" columns={unpaid_shopify_cols} 
							  search={true} pagination={true} sizePerPage={true} dataSort={true}/>
ReactDOM.render(<ModalCmpnt modalId="shopifyUnpaid" modalTitle="Unpaid Shopify" content={unpaid_shopify} wide={true}/>, 
				document.getElementById('bookkeeping.unpaidShopify'))


var shopify_comp_cols = [{'fld': 'label', 'label': 'Label'},
		                 {'fld': 'payout_date', 'label': 'Date', formatter: formatters.date},
		                 {'fld': 'payout', 'label': 'Payout', formatter: formatters.number},
		                 {'fld': 'calcd_payout', 'label': 'Savor Calc', formatter: formatters.number},
		                 {'fld': 'diff', 'label': 'Diff', formatter: formatters.number}
		                 ]
var shopify_comparison = <BSTable source="/api/sales/payout_comp/SHOPIFY/?raw=true" columns={shopify_comp_cols} 
								  search={true} pagination={true} sizePerPage={true} bordered={true}
								  dataSort={true}/>
ReactDOM.render(<ModalCmpnt modalId="shopifyComp" modalTitle="Shopify Payouts" wide={true} content={shopify_comparison} wide={true}/>, 
				document.getElementById('bookkeeping.shopifyComp'))
