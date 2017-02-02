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


var FRB_uploader = <Uploader instructions={FRB_upload_help} postUrl={'/importers/upload/frb/'}/>
ReactDOM.render(<ModalCmpnt modalId="FRBuploader" modalTitle="FRB File Upload" content={FRB_uploader}/>, document.getElementById('bookkeeping.upload.FRB'))


var UPS_uploader = <Uploader instructions={UPS_upload_help} postUrl={'/importers/upload/ups/'}/>
ReactDOM.render(<ModalCmpnt modalId="UPSuploader" modalTitle="UPS File Upload" content={UPS_uploader}/>, document.getElementById('bookkeeping.upload.UPS'))


var mcard_uploader = <Uploader instructions={'Expects an ofx or qfx file with headers: Date, ABA Num, Currency, Account Num, Account Name, Description, BAI Code, Amount, Serial Num, Ref Num'} 
						 postUrl={'/importers/upload/mcard/'}/>
ReactDOM.render(<ModalCmpnt modalId="MCARDuploader" modalTitle="Mastercard File Upload" content={mcard_uploader}/>, document.getElementById('bookkeeping.upload.MCARD'))


var IFS_uploader = <Uploader instructions={'Expects a csv file with at least following headers: ID Reg (*) and Statement Number'} 
						 postUrl={'/importers/upload/IFSmonthly/'}/>
ReactDOM.render(<ModalCmpnt modalId="IFSuploader" modalTitle="IFS Statement Upload" content={IFS_uploader}/>, document.getElementById('bookkeeping.upload.IFS'))


var last_uploads_cols  = [{'fld': 'Upload', 'label': 'Upload Name'},
					 	  {'fld': 'Last Upload', 'label': 'Uploaded Thru', formatter: formatters.date}
					 	  ]

var last_uploads = <BSTable source="/api/reports/last_uploads/?raw=true" columns={last_uploads_cols} />
ReactDOM.render(last_uploads, document.getElementById('bookkeeping.lastUploads'))


var payables_cols  = [{'fld': 'counterparty', 'counterparty': 'Upload Name'},
					 	  {'fld': 'amount', 'label': 'Amount', formatter: formatters.drill}
					 	  ]

var payables = <BSTable source="/api/reports/payables/?raw=true" columns={payables_cols} />
ReactDOM.render(payables, document.getElementById('bookkeeping.payables'))



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
				document.getElementById('bookkeeping.fulfillNoShipcharge'))


var ups_invoices_cols = [{'fld': 'invoice_number', 'label': 'Invoice #'},
		                 {'fld': 'last_date', 'label': 'Sale Date', formatter: formatters.date},
		                 {'fld': 'charge', 'label': 'Amount'}
		                 ]

var ups_invoices = <BSTable source="/api/fulfill/UPS_invoices/?raw=true" columns={ups_invoices_cols} 
							search={true} pagination={true} sizePerPage={true} bordered={true}
							dataSort={true}/>
ReactDOM.render(<ModalCmpnt modalId="upsInvoices" modalTitle="UPS Invoices" content={ups_invoices}/>, 
				document.getElementById('bookkeeping.upsInvoices'))



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
				document.getElementById('bookkeeping.misBilledUPS'))
