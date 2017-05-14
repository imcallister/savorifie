import React, {Component} from 'react';

import Table from '../components/Table';

var rows = []
 
const onChange = (row) => {
  console.log(row);
};

const get_row = (row, headers) => {
    
    var output = headers.map(function(h) {
        var formatter = h.formatter;
        return (formatter ? formatter(row[h.fld]) : row[h.fld]);
    });
    return output;
    };


class TableContainer extends React.Component {
    
  
    constructor() {
      super();
      this.state = { tableData: [] , rows: []}
    }

    componentWillMount() {
      this.serverRequest = $.get(this.props.source, function (result) {
        this.setState({
          tableData: result,
          rows: result.map(r => get_row(r, this.props.headers))
        });
      }.bind(this));
    }

    componentWillUnmount() {
      this.serverRequest.abort();
    }

    
    render() {
        return (
          <Table
            onChange={onChange}
            rows={this.state.rows}
            headers={this.props.headers}
          />
      );
    }
}

module.exports = TableContainer;
