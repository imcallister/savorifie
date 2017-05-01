var React = require('react')
var ReactDOM = require('react-dom')

var JobDisplay = require('../containers/loadJobContainer') 
var ModalCmpnt = require('../components/modalCmpnt')
var formatters = require('../helpers/formatters')
var BSTable = require('../containers/acctifieTableContainer')

var last_uploads_cols  = [{'fld': 'Upload', 'label': 'Upload Name'},
					 	  {'fld': 'Last Upload', 'label': 'Uploaded Thru', formatter: formatters.date}
					 	  ]

var last_uploads = <BSTable source="/api/reports/order_loads/?raw=true" columns={last_uploads_cols} />
ReactDOM.render(last_uploads, document.getElementById('fulfillment.lastUploads'))


var FBA_downloader = <JobDisplay postUrl={'/importers/upload/FBA/'}/>
ReactDOM.render(<ModalCmpnt modalId="FBAdownloader" modalTitle="FBA Data Download" content={FBA_downloader}/>, document.getElementById('fulfillment.download.FBA'))

var Shopify_orders_downloader = <JobDisplay postUrl={'/importers/upload/shopify_orders/'}/>
ReactDOM.render(<ModalCmpnt modalId="ShopifyOrdersdownloader" modalTitle="Shopify Order Download" content={Shopify_orders_downloader}/>, document.getElementById('fulfillment.download.shopify_orders'))
