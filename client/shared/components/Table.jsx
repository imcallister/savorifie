import React, {Component} from 'react';
import {Table, TableBody, TableHeader, TableHeaderColumn, TableRow, TableRowColumn} from 'material-ui/Table';


class MUITableRow extends Component {
    render() {
        var i = this.props.index;
        return (
            <TableRow selectable={true} key={'r'+i}>
                {this.props.flds.map((rc, j) => <TableRowColumn key={'rc'+i+j}>{rc}</TableRowColumn>)}
            </TableRow>
        )
    }
}


export default class MUITable extends Component {
    state = {
        fixedHeader: true,
        fixedFooter: true,
        stripedRows: false,
        showRowHover: false,
        selectable: true,
        multiSelectable: false,
        enableSelectAll: false,
        deselectOnClickaway: true,
        showCheckboxes: true,
        height: '300px',
      };

    render() {
        return (
            <Table selectable={false}>
                <TableHeader displaySelectAll={false}
                             adjustForCheckbox={false}>
                    <TableRow>
                        {this.props.headers.map((h, j) => <TableHeaderColumn tooltip="Hello"  key={'hc'+j} >{h.label}</TableHeaderColumn>)}
                    </TableRow>
                </TableHeader>
                <TableBody displayRowCheckbox={false} stripedRows={this.state.stripedRows}>
                    {this.props.rows.map((r, i) => <MUITableRow key={'row'+i} index={i} flds={r} />)}
                </TableBody>
            </Table>
        );
    }
}
