var simpleChart = function(dataUrl, renderAt, chartTitle, chartType, seriesNames) {

     var chartDef = {
        chart: {
            renderTo: renderAt,
            type: chartType,
        },
        legend: {enabled: true},
        title: {text: chartTitle},
        xAxis: {title: {text: null}},
        yAxis: {title: {text: null}},
        series: Array.apply(null, {length: seriesNames.length}).map(function() {return {};}),
        credits: {
            enabled: false
        }
    };

    $.ajax({
        type: 'get',
        url: dataUrl,
        success:function(data) {

            chartDef.xAxis.categories = data['chart_data']['x_points'];
            for (i=0; i < seriesNames.length; i++) {
                chartDef.series[i].name = seriesNames[i];
                chartDef.series[i].data = data['chart_data']['values'][i];
            }
            var chart = new Highcharts.Chart(chartDef);
        }
    });

};

var simpleChart2 = function(dataUrl, renderAt, chartTitle, seriesTypes, seriesAxis, seriesNames, yAxisNames) {

     var chartDef = {
        chart: {
            renderTo: renderAt,
        },
        legend: {enabled: true},
        title: {text: chartTitle},
        xAxis: {title: {text: null}},
        yAxis: [{title: {text: yAxisNames[0]}, min:0}, {title: {text: yAxisNames[1]}, opposite: true, min:0}],
        series: Array.apply(null, {length: seriesNames.length}).map(function() {return {};}),
        credits: {
            enabled: false
        }
    };

    $.ajax({
        type: 'get',
        url: dataUrl,
        success:function(data) {

            chartDef.xAxis.categories = data['chart_data']['x_points'];
            for (i=0; i < seriesNames.length; i++) {
                chartDef.series[i].name = seriesNames[i];
                chartDef.series[i].type = seriesTypes[i];
                chartDef.series[i].yAxis = seriesAxis[i];
                chartDef.series[i].data = data['chart_data']['values'][i];
            }
            var chart = new Highcharts.Chart(chartDef);
        }
    });

};


var stackedChart = function(dataUrl, renderAt, chartTitle, chartType, seriesAxis) {

     var chartDef = {
        chart: {
            renderTo: renderAt,
            type: chartType,
        },
        legend: {enabled: true},
        plotOptions: {column: {stacking: 'normal'}},
        title: {text: chartTitle},
        xAxis: {title: {text: null}},
        yAxis: [{title: {text: null}, min:0}, {title: {text: null}, opposite: true, min:0}],
        series: Array.apply(null, {length: seriesAxis.length}).map(function() {return {};}),
        credits: {
            enabled: false
        }
    };

    $.ajax({
        type: 'get',
        url: dataUrl,
        success:function(data) {

            chartDef.xAxis.categories = data['chart_data']['x_points'];
            
            stacks = ['left axis', 'right axis']
            for (i=0; i < seriesAxis.length; i++) {
                chartDef.series[i].data = data['chart_data']['values'][i];
                chartDef.series[i].stack = stacks[seriesAxis[i]];
                chartDef.series[i].name = data['chart_data']['series_names'][i];
                chartDef.series[i].yAxis = seriesAxis[i];
            }
            var chart = new Highcharts.Chart(chartDef);
        }
    });

};

var doubleAxisChart = function(dataUrl, renderAt, chartTitle, chartType, seriesNames, seriesAxis, yAxisNames) {

     var chartDef = {
        chart: {
            renderTo: renderAt,
            type: chartType,
        },
        legend: {enabled: true},
        title: {text: chartTitle},
        xAxis: {title: {text: null}},
        yAxis: [{title: {text: yAxisNames[0]}, min:0}, {title: {text: yAxisNames[1]}, opposite: true, min:0}],
        series: Array.apply(null, {length: seriesNames.length}).map(function() {return {};}),
        credits: {
            enabled: false
        }
    };

    $.ajax({
        type: 'get',
        url: dataUrl,
        success:function(data) {
            chartDef.xAxis.categories = data['chart_data']['x_points'];
            for (i=0; i < seriesNames.length; i++) {
                chartDef.series[i].name = seriesNames[i];
                chartDef.series[i].data = data['chart_data']['values'][i];
                chartDef.series[i].yAxis = seriesAxis[i];
            }
            var chart = new Highcharts.Chart(chartDef);
        }
    });

};

var multiLineChart = function(dataUrl, renderAt, chartTitle) {
    var chartDef = {
        chart: {
          renderTo: renderAt
        },
        title: {
            text: chartTitle
        },
        xAxis: {
            categories: []
        },
        series: []
    };

    $.ajax({
      type: 'get',
      url: dataUrl,
      success:function(data) {
          console.log(data);
          chartDef.xAxis.categories = data['chart_data']['x_points'];
          for (i=0; i < data.chart_data.series.length; i++) {
              chartDef.series[i] = {
                name: data['chart_data']['series'][i]['name'],
                data: data['chart_data']['series'][i]['values']
              }
          }
          var chart = new Highcharts.Chart(chartDef);
      }
    });
};




var cash_bals_chart = function(data_url, renderTo) {    
        
     var avgByDayOptions2 = {
        chart: {
            renderTo: renderTo,
            type: 'line',
        },


        legend: {enabled: true},
        title: {text: 'Cash Balances'},
        subtitle: {text: 'Last month'},
        xAxis: {title: {text: null}, labels: {rotation: -45}, type:'datetime'},
        yAxis: {title: {text: null}},
        series: [{}],
        credits: {
            enabled: false
        }
    };

    $.ajax({
        type: 'get',
        url: data_url,
        success:function(data) {
            avgByDayOptions2.xAxis.categories = data['chart_data']['dates'];
            avgByDayOptions2.series[0].name = 'SAV Cash';
            avgByDayOptions2.series[0].data = data['chart_data']['values']['SAV'];

            var chart = new Highcharts.Chart(avgByDayOptions2);
        }
    });

};

var expense_trends = function(data_url, renderTo) {
     var avgByDayOptions4 = {
        chart: {
            renderTo: renderTo,
            type: 'column',
        },
        title: {
                text: null
            },
        xAxis: {},
        yAxis: {
            min: 0,
            title: {
                text: null
            },
            stackLabels: {
                enabled: true,
                style: {
                    fontWeight: 'bold',
                    color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                }
            }
        },
        legend: {
            align: 'right',
            x: 0,
            verticalAlign: 'bottom',
            y: 0,
            floating: false,
            backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || 'white',
            borderColor: '#CCC',
            borderWidth: 1,
            shadow: false
        },
        tooltip: {
            formatter: function () {
                return '<b>' + this.x + '</b><br/>' +
                    this.series.name + ': ' + this.y + '<br/>' +
                    'Total: ' + this.point.stackTotal;
            }
        },
        plotOptions: {
            column: {
                stacking: 'normal',
                dataLabels: {
                    enabled: false,
                    color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white',
                    style: {
                        textShadow: '0 0 3px black'
                    }
                }
            }
        },
        credits: {
            enabled: false
        }
    };
    

    $.ajax({
        type: 'get',
        url: data_url,
        success:function(data) {
            avgByDayOptions4.xAxis.categories = data['chart_data']['dates'];
            
            avgByDayOptions4.series = [];

            var data_series = data['chart_data']['values'];

            for (var key in data_series) {
                avgByDayOptions4.series.push({'name': key, 'data': data_series[key]})
            }
            
            var chart = new Highcharts.Chart(avgByDayOptions4);
        }
    });
};
