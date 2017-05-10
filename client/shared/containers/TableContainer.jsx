import React, {Component} from 'react';

import EditTable  from 'material-ui-table-edit';  



var rows = []
 
const onChange = (row) => {
  console.log(row);
}

class TableContainer extends React.Component {
    
  /*
    constructor() {
      super();
      this.state = { tableData: [] }
    }


    componentDidMount() {
      this.serverRequest = $.get(this.props.source, function (result) {
        this.setState({
          tableData: result
        });
      }.bind(this));
    }

    componentWillUnmount() {
      this.serverRequest.abort();
    }
    */

    get_rows() {
      console.log('in get_rows');
      console.log(this.props.data);

      var output = this.props.data.map(function(r) {return this.get_row(r);}.bind(this));
      console.log('DONE DONE', output);
      return output;
    }

    get_row(row) {
      var output = this.props.headers.map(function(h) {
          return row[h.value];
        });
      console.log('DONE', output);
      return output;
    }

    render() {
      console.log('render');
      //var rows = this.get_rows();
      console.log('DONE3', rows);
          
      return (
          <EditTable
            onChange={onChange}
            rows={this.state.rows}
            headerColumns={this.props.headers}
          />
      );
    }
}

module.exports = TableContainer;
