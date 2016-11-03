var React = require('react');
var Highcharts = require('highcharts');

class Chart extends React.Component {
  constructor() {
    super();
  }

  render() {
    if (this.props.loaded) {
      this.chart = new Highcharts["Chart"](this.props.chartName, this.props.data);
    }

    return <div id={this.props.chartName}></div> 
  }
}

module.exports = Chart;