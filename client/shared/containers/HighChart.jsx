import React, { Component } from 'react';
import fetch from 'isomorphic-fetch';

import HighChart from '../components/HighCharts';  
import { checkHttpStatus, parseJSON } from '../../utils';

export default class HighChartContainer extends Component {

    constructor() {
      super();
      this.state = {loaded: false};
      this.state.data = { series: [], x_vals: []};
    }

    componentDidMount() {
        fetch(this.props.source, {
            credentials: 'include',
            mode: 'no-cors',
            headers: {
                Accept: 'application/json',
                Authorization: `Token ${this.props.token}`
            }
        })
        .then(checkHttpStatus)
        .then(parseJSON)
        .then((response) => {
            this.setState({
              data: response,
              loaded: true
            });
        });

    }
    

    render() {
      return (
          <HighChart data={this.state.data} chartName={this.props.chartName} loaded={this.state.loaded} />
      )
    }
}
