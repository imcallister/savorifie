var React = require('react');

var AcctifieTable = require('../components/acctifieTable');  


class DataTableContainer extends React.Component {
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


    render() {
      return (
          <AcctifieTable tableData={this.state.tableData} columns={this.props.columns} search={this.props.search} pagination={this.props.pagination} sizePerPage={this.props.pageSize}>
          </AcctifieTable>
      );
    }
}

module.exports = DataTableContainer;
