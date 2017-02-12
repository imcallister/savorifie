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


var mcard_uploader = <Uploader instructions={'Expects an ofx or qfx file with headers: Date, ABA Num, Currency, Account Num, Account Name, Description, BAI Code, Amount, Serial Num, Ref Num'} 
						 postUrl={'/importers/upload/mcard/'}/>
ReactDOM.render(<ModalCmpnt modalId="MCARDuploader" modalTitle="Mastercard File Upload" content={mcard_uploader}/>, document.getElementById('bookkeeping.upload.MCARD'))


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