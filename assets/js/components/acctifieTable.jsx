var React = require('react');

var ReactBSTable = require('react-bootstrap-table');  
var BootstrapTable = ReactBSTable.BootstrapTable;
var TableHeaderColumn = ReactBSTable.TableHeaderColumn;



class DataTable extends React.Component {
  constructor() {
    super();
  }

  render() {
    return (
      <BootstrapTable data={this.props.tableData} striped={true} hover={true} search={true}>
        {this.props.columns.map(function(col, index) {
            renderColumn({col})         
        })}
      </BootstrapTable>
    );
  }

  renderColumn(col) {
    var props = {};
    props.isKey = false;
    if (index==0) {
      props.isKey = true;
    }
    if (col.formatter) {
      props.dataFormat = col.formatter;
    }
    return <TableHeaderColumn dataField={col.fld} key={index} {...props} dataSort={true}>{col.label}</TableHeaderColumn> 
  }

};

export default DataTable;
