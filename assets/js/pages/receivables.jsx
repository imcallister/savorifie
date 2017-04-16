var React = require('react')
var ReactDOM = require('react-dom')

var BHelp = require('../help_text/bookkeeping') 
var BSTable = require('../containers/acctifieTableContainer')
var Uploader = require('../containers/uploaderContainer') 
var formatters = require('../helpers/formatters')
var ModalCmpnt = require('../components/modalCmpnt')





var Shopify_uploader = <Uploader instructions="" postUrl={'/importers/upload/shopify_payouts/'}/>
ReactDOM.render(<ModalCmpnt modalId="SHOPIFYPayoutUploader" modalTitle="Shopify Payout File Upload" content={Shopify_uploader}/>, document.getElementById('bookkeeping.upload.SHOPIFYPayoutUploader'))




var receivables_cols  = [{'fld': 'counterparty', 'counterparty': 'Upload Name'},
					 	  {'fld': 'amount', 'label': 'Amount', formatter: formatters.drill}
					 	  ]

var receivables = <BSTable source="/api/reports/receivables/?raw=true" columns={receivables_cols} />
ReactDOM.render(receivables, document.getElementById('bookkeeping.receivables'))


var future_receivables = <BSTable source="/api/reports/future_receivables/?raw=true" columns={receivables_cols} />
ReactDOM.render(future_receivables, document.getElementById('bookkeeping.futurereceivables'))


var unpaid_cols  = [{'fld': 'label', 'label': 'ID'},
			        {'fld': 'sale_date', 'label': 'Date', formatter: formatters.date},
			        {'fld': 'shipping_name', 'label': 'Name'},
			        {'fld': 'proceeds', 'label': 'Proceeds'},
			        {'fld': 'unpaid', 'label': 'Unpaid'},
			        {'fld': 'items_string', 'label': 'SKUs'}
			        ]

var unpaid_shopify = <BSTable source="/api/sales/proceeds_rec/?paid_thru=SHOPIFY&raw=true" columns={unpaid_cols} 
							  search={true} pagination={true} sizePerPage={true} dataSort={true}/>
ReactDOM.render(<ModalCmpnt modalId="shopifyUnpaid" modalTitle="Unpaid Shopify" content={unpaid_shopify} wide={true}/>, 
				document.getElementById('bookkeeping.unpaidShopify'))

var unpaid_paypal = <BSTable source="/api/sales/proceeds_rec/?paid_thru=PAYPAL&raw=true" columns={unpaid_cols} 
							  search={true} pagination={true} sizePerPage={true} dataSort={true}/>
ReactDOM.render(<ModalCmpnt modalId="paypalUnpaid" modalTitle="Unpaid Paypal" content={unpaid_paypal} wide={true}/>, 
				document.getElementById('bookkeeping.unpaidPaypal'))


var unpaid_amazonPayments = <BSTable source="/api/sales/proceeds_rec/?paid_thru=AMZN_PMTS&raw=true" columns={unpaid_cols} 
							  search={true} pagination={true} sizePerPage={true} dataSort={true}/>
ReactDOM.render(<ModalCmpnt modalId="amazonPaymentsUnpaid" modalTitle="Unpaid Amazon Payments" content={unpaid_amazonPayments} wide={true}/>, 
				document.getElementById('bookkeeping.unpaidAmazonPayments'))


var unpaid_amazonFBA = <BSTable source="/api/sales/proceeds_rec/?paid_thru=AMZN&raw=true" columns={unpaid_cols} 
							  search={true} pagination={true} sizePerPage={true} dataSort={true}/>
ReactDOM.render(<ModalCmpnt modalId="amazonFBAUnpaid" modalTitle="Unpaid Amazon FBA" content={unpaid_amazonFBA} wide={true}/>, 
				document.getElementById('bookkeeping.unpaidAmazonFBA'))


var unpaid_buybuy = <BSTable source="/api/sales/proceeds_rec/?paid_thru=BUYBUY&raw=true" columns={unpaid_cols} 
							  search={true} pagination={true} sizePerPage={true} dataSort={true}/>
ReactDOM.render(<ModalCmpnt modalId="buyBuyUnpaid" modalTitle="Unpaid Buy Buy" content={unpaid_buybuy} wide={true}/>, 
				document.getElementById('bookkeeping.unpaidBuyBuy'))


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
