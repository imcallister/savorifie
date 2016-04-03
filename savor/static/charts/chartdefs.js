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
