var React = require('react');
var Highcharts = require('highcharts');

class Chart extends React.Component {
  constructor() {
    super();
  }

  componentDidMount() {
    var data = this.props.data;
    var occupation = this.props.occupation;
    $('.hccontainer').highcharts({
        chart: {
            type: 'bar'
        },
        title: {
            text: 'StackOverflow 2016 Developer Survey Results for Occupation'
        },
        xAxis: {
            categories: occupation
        },
        yAxis: {
            title: {
                text: 'Percentage of Respondants'
            }
        },
        plotOptions: {
          series: {
            dataLabels: {
              enabled: true,
              formatter: function() {
              return Highcharts.numberFormat(this.y) + '%';
            }
            },
          }
        },
        chart: {
          type: "bar"
        },
        series: [{
            name: 'Developer Occupations',
            data: data
        }]
    });   
  }

  componentWillReceiveProps() {
    var data = this.props.data;
    var occupation = this.props.occupation;
     $('.hccontainer').highcharts({
        chart: {
            type: 'bar'
        },
        title: {
            text: 'StackOverflow 2016 Developer Survey Results for Occupation'
        },
        xAxis: {
            categories: occupation
        },
        yAxis: {
            title: {
                text: 'Percentage of Respondants'
            }
        },
        plotOptions: {
          series: {
            dataLabels: {
              enabled: true,
              formatter: function() {
              return Highcharts.numberFormat(this.y) + '%';
            }
            },
          }
        },
        chart: {
          backgroundColor: "#FCFFC5",
          type: "bar"
        },
        series: [{
            name: 'Developer Occupations',
            data: data
        }]
    });
  }
  
  render() {
    var style = {
      marginTop: "25px",
      marginBottom: "0px"
    };
    return (
      <div
        style={style}
        className="hccontainer">
      </div>
    )
  }
}

module.exports = Chart;