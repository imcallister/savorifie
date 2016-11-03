var React = require('react');
var Highcharts = require('highcharts');

class Chart extends React.Component {
  constructor() {
    super();
  }

  
  componentDidMount() {
    var options = this.props.config;
    options.xAxis = {categories: this.props.data.x_vals};
    options.series = this.props.data.series;
    
    this.chart = new Highcharts["Chart"](
            this.props.chartName, 
            this.props.config
        );
  }


  render() {
    if (this.props.loaded) {
      var options = this.props.config;
      options.xAxis = {categories: this.props.data.x_vals};
      options.series = this.props.data.series;
      this.chart = new Highcharts["Chart"](this.props.chartName, options);
    }

    return <div id={this.props.chartName}></div> 
  }
}

module.exports = Chart;