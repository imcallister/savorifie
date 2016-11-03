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
        this.setState({
          data: result,
          loaded: true
        });
      }.bind(this));
    }
    

    render() {
      return (
          <HighChart data={this.state.data} chartName={this.props.chartName} loaded={this.state.loaded} />
      )
    }
}

module.exports = HChartContainer;
