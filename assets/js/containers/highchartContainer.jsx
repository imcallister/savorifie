var React = require('react');

var HighChart = require('../components/highchartCmpnt');  


class HChartContainer extends React.Component {

    constructor() {
      super();
      this.state = {loaded: false};
      this.state.data = { series: [], x_vals: []};
    }

    componentDidMount() {
      this.serverRequest = $.get(this.props.source, function (result) {
        
        for (var i=0; i < result.series.length; i++) {
          result.series[i].data = result.series[i].data.map(function(x) {return Number(x)})
        };

        this.setState({
          data: result,
          loaded: true
        });
      }.bind(this));
    }
    

    render() {
      return (
          <HighChart data={this.state.data} chartName={this.props.chartName} loaded={this.state.loaded} config={this.props.config} />
      )
    }
}

module.exports = HChartContainer;
