var React = require('react');

var ReactBSTable = require('react-bootstrap-table');  
var BootstrapTable = ReactBSTable.BootstrapTable;
var TableHeaderColumn = ReactBSTable.TableHeaderColumn;



var RemoteTable = React.createClass({
    getInitialState: function() {
      return {
        myTableData: []
      };
    },

    componentDidMount: function() {
      this.serverRequest = $.get(this.props.source, function (result) {
        this.setState({
          myTableData: result
        });
      }.bind(this));
    },

    componentWillUnmount: function() {
      this.serverRequest.abort();
    },


    render: function() {
        function priceFormatter(cell, row){
          return '<i class="glyphicon glyphicon-usd"></i> ' + cell;
        };

        return (
          <BootstrapTable data={this.state.myTableData} striped={true} hover={true}>
              <TableHeaderColumn dataField="invoice_number" isKey={true} dataAlign="center" dataSort={true}>Product ID</TableHeaderColumn>
              <TableHeaderColumn dataField="last_date" dataSort={true}>Product Name</TableHeaderColumn>
              <TableHeaderColumn dataField="charge" dataFormat={priceFormatter}>Product Price</TableHeaderColumn>
          </BootstrapTable>
        );
    }
});

module.exports = RemoteTable;
