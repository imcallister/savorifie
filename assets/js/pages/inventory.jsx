var React = require('react')
var ReactDOM = require('react-dom')
var SwatchRow = require('../containers/swatchRowContainer');
var Highcharts = require('../containers/highchartContainer');


var SWATCHES = [{color: 'dbpanel-plum', item: 'SYE1'},
	            {color: 'dbpanel-ocean', item: 'SYE2'},
	            {color: 'dbpanel-slate', item: 'SYE3'},
	            {color: 'dbpanel-plum', item: 'BE1'},
	            {color: 'dbpanel-ocean', item: 'BE2'},
	            {color: 'dbpanel-slate', item: 'BE3'},
]


ReactDOM.render(<SwatchRow swatches={SWATCHES} source='/api/inventory/locationinventory/NC2/?raw=true' />, document.getElementById("inventory.NC2.inventory"));
ReactDOM.render(<SwatchRow swatches={SWATCHES} source='/api/inventory/locationinventory/152Frank/?raw=true' />, document.getElementById("inventory.152Frank.inventory"));
ReactDOM.render(<SwatchRow swatches={SWATCHES} source='/api/inventory/locationinventory/LAPort/?raw=true' />, document.getElementById("inventory.LAPort.inventory"));

ReactDOM.render(<Highcharts chartName="inventory.totalsales" source="/chart/sales/sale_count/"/>, document.getElementById("inventory.totalsales"));


