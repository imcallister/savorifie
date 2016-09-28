var React = require('react');
var RespFixedDataTable = require('responsive-fixed-data-table');
const {Table, Column, Cell} = require('fixed-data-table');


class MyTable extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      myTableData: [
        {name: 'Rylan', 'count': 3},
        {name: 'Amelia', 'count': 3},
        {name: 'Estevan', 'count': 3},
        {name: 'Florence', 'count': 3},
        {name: 'Tressa', 'count': 3},
      ],
    };
  }

  render() {
    return (
      <Table
        rowsCount={this.state.myTableData.length}
        rowHeight={30}
        headerHeight={40}
        width={400}
        maxHeight={500}
        >
        <Column
          header={<Cell>Name</Cell>}
          cell={props => (
            <Cell {...props}>
              {this.state.myTableData[props.rowIndex].name}
            </Cell>
          )}
          width={100}
        
        />
        <Column
          header={<Cell>Count</Cell>}
          cell={props => (
            <Cell {...props}>
              {this.state.myTableData[props.rowIndex].count}
            </Cell>
          )}
          width={100}
        
        />
        <Column
          header={<Cell>Count</Cell>}
          cell={props => (
            <Cell {...props}>
              {this.state.myTableData[props.rowIndex].count}
            </Cell>
          )}
          width={100}
        
        />
      </Table>
    );
  }
};

module.exports = MyTable;