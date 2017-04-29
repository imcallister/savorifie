var React = require('react')
var ReactDOM = require('react-dom')

var JobDisplay = require('../containers/loadJobContainer') 
var ModalCmpnt = require('../components/modalCmpnt')



var FBA_downloader = <JobDisplay postUrl={'/importers/upload/FBA/'}/>
ReactDOM.render(<ModalCmpnt modalId="FBAdownloader" modalTitle="FBA Data Download" content={FBA_downloader}/>, document.getElementById('fulfillment.download.FBA'))

var Shopify_orders_downloader = <JobDisplay postUrl={'/importers/upload/shopify_orders/'}/>
ReactDOM.render(<ModalCmpnt modalId="ShopifyOrdersdownloader" modalTitle="Shopify Order Download" content={Shopify_orders_downloader}/>, document.getElementById('fulfillment.download.shopify_orders'))
