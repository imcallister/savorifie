var React = require('react')
var ReactDOM = require('react-dom')

var JobDisplay = require('../containers/loadJobContainer') 
var ModalCmpnt = require('../components/modalCmpnt')



var FBA_downloader = <JobDisplay postUrl={'/importers/upload/FBA/'}/>
ReactDOM.render(<ModalCmpnt modalId="FBAdownloader" modalTitle="FBA Data Download" content={FBA_downloader}/>, document.getElementById('fulfillment.download.FBA'))
