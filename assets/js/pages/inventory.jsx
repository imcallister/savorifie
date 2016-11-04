var React = require('react')
var ReactDOM = require('react-dom')
var SwatchRow = require('../containers/swatchRowContainer');
var Highcharts = require('../containers/highchartContainer');


var SWATCHES = [{color: 'panel-plum', item: 'SYE1'},
	            {color: 'panel-ocean', item: 'SYE2'},
	            {color: 'panel-slate', item: 'SYE3'},
	            {color: 'panel-plum', item: 'BE1'},
	            {color: 'panel-ocean', item: 'BE2'},
	            {color: 'panel-slate', item: 'BE3'},
]

ReactDOM.render(<SwatchRow swatches={SWATCHES} source='/api/sales/sale_count/?raw=true' />, document.getElementById("inventory.salecount"));
ReactDOM.render(<SwatchRow swatches={SWATCHES} source='/api/inventory/locationinventory/NC2/?raw=true' />, document.getElementById("inventory.NC2.inventory"));
ReactDOM.render(<SwatchRow swatches={SWATCHES} source='/api/inventory/locationinventory/152Frank/?raw=true' />, document.getElementById("inventory.152Frank.inventory"));
ReactDOM.render(<SwatchRow swatches={SWATCHES} source='/api/inventory/locationinventory/MICH/?raw=true' />, document.getElementById("inventory.MICH.inventory"));
ReactDOM.render(<SwatchRow swatches={SWATCHES} source='/api/inventory/locationinventory/SAG/?raw=true' />, document.getElementById("inventory.SAG.inventory"));

ReactDOM.render(<Highcharts chartName="inventory.totalsales" source="/chart/sales/sale_count/"/>, document.getElementById("inventory.totalsales"));


