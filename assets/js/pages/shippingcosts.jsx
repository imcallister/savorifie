var React = require('react')
var ReactDOM = require('react-dom')

var UPSHelp = require('../help_text/UPS_upload')
var BSTable = require('../containers/acctifieTableContainer')
var Uploader = require('../containers/uploaderContainer') 
var formatters = require('../helpers/formatters')
var ModalCmpnt = require('../components/modalCmpnt')


var UPS_upload_help = <UPSHelp/>

var UPS_uploader = <Uploader instructions={UPS_upload_help} postUrl={'/importers/upload/ups/'}/>
ReactDOM.render(<ModalCmpnt modalId="UPSuploader" modalTitle="UPS File Upload" content={UPS_uploader}/>, document.getElementById('shippingcosts.upload.UPS'))


var IFS_uploader = <Uploader instructions={'Expects a csv file with at least following headers: ID Reg (*) and Statement Number'} 
						 postUrl={'/importers/upload/IFSmonthly/'}/>
ReactDOM.render(<ModalCmpnt modalId="IFSuploader" modalTitle="IFS Statement Upload" content={IFS_uploader}/>, document.getElementById('shippingcosts.upload.IFS'))

var bulkShip_uploader = <Uploader instructions={'Expects a csv file with at least following headers: .......'} 
						 postUrl={'/importers/upload/bulk_shipping/'}/>
ReactDOM.render(<ModalCmpnt modalId="BulkShipuploader" modalTitle="IFS Statement Upload" content={bulkShip_uploader}/>, document.getElementById('shippingcosts.upload.bulkShip'))


var last_uploads_cols  = [{'fld': 'Upload', 'label': 'Upload Name'},
					 	  {'fld': 'Last Upload', 'label': 'Uploaded Thru', formatter: formatters.date}
					 	  ]

var last_uploads = <BSTable source="/api/reports/last_uploads/?raw=true" columns={last_uploads_cols} />
ReactDOM.render(last_uploads, document.getElementById('shippingcosts.lastUploads'))



var shipcharge_no_fulfill_cols = [{'fld': 'tracking_number', 'label': 'Tracking Number'},
					              {'fld': 'shipper', 'label': 'Shipper'},
					              {'fld': 'ship_date', 'label': 'Ship Date'},
					              {'fld': 'charge', 'label': 'Charge'}
					            ]
var shipcharge_no_fulfill = <BSTable source="/api/fulfill/shipcharge_no_fulfill/?raw=true" columns={shipcharge_no_fulfill_cols} 
									 search={true} pagination={true} sizePerPage={true} bordered={true}
								  	 dataSort={true}/>    
ReactDOM.render(<ModalCmpnt modalId="shipchargeNoFulfill" modalTitle="Shipping charges missing fulfillment" content={shipcharge_no_fulfill} wide={true}/>, 
				document.getElementById('shippingcosts.shipchargeNoFulfill'))


var no_shipcharge_cols = [{'fld': 'fulfillment_id', 'label': 'Fulfill ID'},
		                 {'fld': 'order', 'label': 'Order'},
		                 {'fld': 'request_date', 'label': 'Request Date', formatter: formatters.date},
		                 {'fld': 'warehouse', 'label': 'Warehouse'},
		                 {'fld': 'ship_type', 'label': 'Ship Type'},
		                 {'fld': 'bill_to', 'label': 'Billing Acct'},
		                 {'fld': 'shipping_name', 'label': 'Ship Name'},
		                 {'fld': 'shipping_company', 'label': 'Shipping Company'}
		                 ]

var fulfill_no_shipcharge = <BSTable source="/api/fulfill/fulfill_no_shipcharge/?raw=true" columns={no_shipcharge_cols} 
									 search={true} pagination={true} sizePerPage={true} bordered={true}
								  	 dataSort={true}/>
ReactDOM.render(<ModalCmpnt modalId="noShipcharge" modalTitle="Fulfillments missing shipping charge" content={fulfill_no_shipcharge} wide={true}/>, 
				document.getElementById('shippingcosts.fulfillNoShipcharge'))


var ups_invoices_cols = [{'fld': 'invoice_number', 'label': 'Invoice #'},
		                 {'fld': 'last_date', 'label': 'Sale Date', formatter: formatters.date},
		                 {'fld': 'charge', 'label': 'Amount'}
		                 ]

var ups_invoices = <BSTable source="/api/fulfill/UPS_invoices/?raw=true" columns={ups_invoices_cols} 
							search={true} pagination={true} sizePerPage={true} bordered={true}
							dataSort={true}/>
ReactDOM.render(<ModalCmpnt modalId="upsInvoices" modalTitle="UPS Invoices" content={ups_invoices}/>, 
				document.getElementById('shippingcosts.upsInvoices'))



var mis_ups_cols = [{'fld': 'tracking_number', 'label': 'Tracking #'},
					{'fld': 'invoice_number', 'label': 'Invoice #'},
		            {'fld': 'ship_date', 'label': 'Ship Date', formatter: formatters.date},
		            {'fld': 'order_related', 'label': 'Amount'},
		            {'fld': 'charge', 'label': 'Amount'},
		            {'fld': 'fulfillment', 'label': 'Fulfillment'},
		            {'fld': 'requested_ship_type', 'label': 'Requested'},
		            {'fld': 'warehouse', 'label': 'Warehouse'},
		                 ]

var mis_ups = <BSTable source="/api/fulfill/UPS_wrong_acct/?raw=true" columns={mis_ups_cols} 
					   search={true} pagination={true} sizePerPage={true} bordered={true}
					   dataSort={true}/>
ReactDOM.render(<ModalCmpnt modalId="misUPS" modalTitle="Mis-billed UPS charges" content={mis_ups}/>, 
				document.getElementById('shippingcosts.misBilledUPS'))
