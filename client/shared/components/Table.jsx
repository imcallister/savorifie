import React, {Component} from 'react';
import {Table, TableBody, TableHeader, TableHeaderColumn, TableRow, TableRowColumn} from 'material-ui/Table';


class MUITableRow extends Component {
    render() {
        const i = this.props.index;
        return (
            <TableRow selectable={true} key={'r'+i}>
                {this.props.flds.map((rc, j) => <TableRowColumn key={'rc'+i+j}>{rc}</TableRowColumn>)}
            </TableRow>
        )
    }
}


export default class MUITable extends Component {
    render() {
        return (
            <Table selectable={false}>
                <TableHeader displaySelectAll={false}
                             adjustForCheckbox={false}>
                    <TableRow>
                        {this.props.headers.map((h, j) => <TableHeaderColumn key={'hc'+j} >{h}</TableHeaderColumn>)}
                    </TableRow>
                </TableHeader>
                <TableBody displayRowCheckbox={false}>
                    {this.props.rows}
                </TableBody>
            </Table>
        );
    }
}
