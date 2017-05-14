import React from 'react';
import { connect } from 'react-redux';

import formatters from '../shared/helpers/formatters';
import TableContainer from '../shared/containers/TableContainer';

var history_headers  = [{fld: 'date', label: 'Date', formatter: formatters.date},
                        {fld: 'id', label: 'id'},
                        {fld: 'comment', label: 'Comment'},
                        {fld: 'account_id', label: 'Account'},
                        {fld: 'counterparty', label: 'Counterparty'},
                        {fld: 'contra_accts', label: 'Contra-Account'},
                        {fld: 'amount', label: 'Amount', formatter: formatters.number},
                        {fld: 'balance', label: 'Balance', formatter: formatters.number}
                          ];


class HistoryView extends React.Component {

    render() {
        return (
            
            <div>
                {this.props.isAuthenticated ?
                    <TableContainer source='${SERVER_URL}/api/reporting/history/3000/?cp=Citibank%20MC&to=2017-05-13&raw=true' headers={history_headers}/>
                    :
                    <div className="margin-top-medium text-center">
                        <p><Link to="/login"><b>Login to access application</b></Link>.</p>
                    </div>
                }
            </div>
        );
    }
}

const mapStateToProps = (state) => {
    return {
        userName: state.auth.userName,
        statusText: state.auth.statusText,
        isAuthenticated: state.auth.isAuthenticated,
    };
};

export default connect(mapStateToProps)(HistoryView);
export { HistoryView as HistoryViewNotConnected };
