var React = require('react')
var ReactDOM = require('react-dom')
var Highcharts = require('../containers/highchartContainer');



ReactDOM.render(<Highcharts chartName="tax.collect" source="/chart/reports/collected_salestax/"/>,
                document.getElementById("highchart.test"));



ReactDOM.render(<Highcharts chartName="tax.collect2" source="/chart/sales/sale_count/"/>,
                document.getElementById("highchart.test2"));

