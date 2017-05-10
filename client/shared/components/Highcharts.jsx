import React, { Component } from 'react';
import Highcharts from'highcharts';

export default class HighChartContainer extends Component {
  
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
