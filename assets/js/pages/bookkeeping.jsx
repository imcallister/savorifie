var React = require('react')
var ReactDOM = require('react-dom')

var BHelp = require('../components/book_help') 
var BSTable = require('../containers/acctifieTableContainer')
var formatters = require('../helpers/formatters')
var ModalCmpnt = require('../components/modalCmpnt')

ReactDOM.render(<BHelp/>, document.getElementById('the-help'));


var tbl_columns = [{'fld': 'invoice_number', 'label': 'Invoice #'},
                   {'fld': 'last_date', 'label': 'Last Date', formatter: formatters.date},
                   {'fld': 'charge', 'label': 'Charge', formatter: formatters.price}
                   ]

ReactDOM.render(<BSTable source="/api/fulfill/UPS_invoices/?raw=true"
                         columns={tbl_columns} />, document.getElementById('the-help2'));




var unpaid_shopify_cols  = [{'fld': 'label', 'label': 'ID'},
			                {'fld': 'channel', 'label': 'Channel'},
			                {'fld': 'sale_date', 'label': 'Date'},
			                {'fld': 'shipping_name', 'label': 'Name'},
			                {'fld': 'shipping_company', 'label': 'Company'},
			                {'fld': 'proceeds', 'label': 'Proceeds'},
			                {'fld': 'items_string', 'label': 'SKUs'}
			                ]

var unpaid_shopify = <BSTable source="/api/sales/unpaid_channel/SHOPIFY/?raw=true" columns={unpaid_shopify_cols} />
ReactDOM.render(<ModalCmpnt modalId="shopifyUnpaid" modalTitle="Unpaid Shopify" content={unpaid_shopify}/>, 
				document.getElementById('bookkeeping.unpaidShopify'))


var shopify_comp_cols = [{'fld': 'id', 'label': 'ID'},
		                 {'fld': 'date', 'label': 'ID'},
		                 {'fld': 'label', 'label': 'Description'},
		                 {'fld': 'payout', 'label': 'Payout'},
		                 {'fld': 'calcd_payout', 'label': 'Savor Calc'},
		                 {'fld': 'diff', 'label': 'Diff'}
		                 ]
var shopify_comparison = <BSTable source="/api/sales/channel_payout_comp/SHOPIFY/?raw=true" columns={shopify_comp_cols} />
ReactDOM.render(<ModalCmpnt modalId="shopifyComp" modalTitle="Shopify Comparison" content={shopify_comparison}/>, 
				document.getElementById('bookkeeping.shopifyComp'))
