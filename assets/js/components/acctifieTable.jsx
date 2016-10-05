var React = require('react');

var ReactBSTable = require('react-bootstrap-table');  
var BootstrapTable = ReactBSTable.BootstrapTable;
var TableHeaderColumn = ReactBSTable.TableHeaderColumn;



class DataTable extends React.Component {
  constructor() {
    super();
  }

  
  render() {
    
    var renderColumn = function(col, index) {
      var props = {};

      props.isKey = (index==0);

      if (col.formatter) {
        props.dataFormat = col.formatter;
      }
      return <TableHeaderColumn dataField={col.fld} key={index} {...props} dataSort={true}>{col.label}</TableHeaderColumn> 
    };

    return (
      <BootstrapTable data={this.props.tableData} striped={true} hover={true} search={true}>
        {this.props.columns.map(renderColumn)}
      </BootstrapTable>
    );
  }
}

module.exports = DataTable;