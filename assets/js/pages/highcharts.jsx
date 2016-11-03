var React = require('react')
var ReactDOM = require('react-dom')
var Highcharts = require('../containers/highchartContainer');


var barConfig = {
        chart: {
            type: 'column'
        },
        title: {
            text: 'Tax Collected'
        },
        yAxis: {
            title: {
                text: 'Total'
            }
        },
        plotOptions: {
          series: {
            dataLabels: {
              enabled: true
            },
          }
        },
        credits: {
            enabled: false
        }
      }


ReactDOM.render(<Highcharts config={barConfig} chartName="tax.collect" source="/api/reports/collected_salestax/?raw=true&chart=true"/>,
                document.getElementById("highchart.test"));


var barConfig2 = {
        chart: {
            type: 'column'
        },
        title: {
            text: 'Unit Sales'
        },
        yAxis: {
            title: {
                text: 'Total'
            }
        },
        plotOptions: {
          series: {
            dataLabels: {
              enabled: true
            },
          }
        },
        credits: {
            enabled: false
        }
      }


ReactDOM.render(<Highcharts config={barConfig2} chartName="tax.collect2" source="/api/sales/sale_count/?raw=true&chart=true"/>,
                document.getElementById("highchart.test2"));

