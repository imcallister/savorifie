import React from 'react';
import { Link } from 'react-router';
import { connect } from 'react-redux';

import HighChartContainer from '../shared/containers/HighChart';  

import './style.scss';
import reactLogo from './images/react-logo.png';
import reduxLogo from './images/redux-logo.png';
import savorLogo from '../shared/images/savor-logo.png';

class HomeView extends React.Component {

    static propTypes = {
        statusText: React.PropTypes.string,
        userName: React.PropTypes.string
    };

    render() {
        return (
            
            <div className="container">
                {this.props.isAuthenticated ?
                    <div className="text-center">
                        <h1>Savorifie Redux</h1>
                        <div className="row">
                            <div className="col-md-6">
                                <div className="panel panel-default">
                                    <div className="panel-heading">
                                        <h3 className="panel-title">Expense Trends</h3>
                                    </div>
                                    <div className="panel-body">
                                        <HighChartContainer chartName="inventory.expense_trends"
                                                            source="/chart/reports/expense_trends/"
                                        />
                                    </div>    
                                </div>
                            </div>
                            
                            <div className="col-md-6">
                                <div className="panel panel-default">
                                    <div className="panel-heading">
                                        <h3 className="panel-title">Cash Balances</h3>
                                    </div>
                                    <div className="panel-body">
                                        <HighChartContainer chartName="inventory.cashbalances"
                                                            source="/chart/reports/cash_balances/"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                
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

export default connect(mapStateToProps)(HomeView);
export { HomeView as HomeViewNotConnected };
