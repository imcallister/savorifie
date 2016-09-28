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
        return (
          <BootstrapTable data={this.state.myTableData} striped={true} hover={true} search={true}>
                {this.props.columns.map(function(col, index) {
                    var props = {};
                    
                    props.isKey = false;
                    if (index==0) {
                        props.isKey = true;
                    }
                    if (col.formatter) {
                        props.dataFormat = col.formatter;
                    }
                    return <TableHeaderColumn dataField={col.fld} key={index} {...props} dataSort={true}>{col.label}</TableHeaderColumn>
                })
            }
          </BootstrapTable>
        );
    }
});

module.exports = RemoteTable;
