import React from 'react';
import { Link } from 'react-router';
import { connect } from 'react-redux';

import HighChartContainer from '../shared/containers/HighChart';
import ReportBuilder from './containers/reportBuilder'

import '../styles/main.scss';
import savorLogo from '../shared/images/savor-logo.png';

class ReportsView extends React.Component {

    static propTypes = {
        statusText: React.PropTypes.string,
        userName: React.PropTypes.string
    };

    render() {
        return (
            
            <div className="container">
                {this.props.isAuthenticated ?
                    <div>
                        <div className="row">
                            <div className="col-md-6">
                                <div className="tab-pane panel panel-default">
                                    <div className="panel-heading">
                                        <h3 className="panel-title">Report Builder</h3>
                                    </div>

                                    <div className="panel-body">
                                        <ReportBuilder/>
                                    </div>
                                </div>

                                <div className="panel panel-default">
                                    <div className="panel-heading">
                                        <h3 className="panel-title">Accounting Quick Links</h3>
                                    </div>
                                    <div className="panel-body">
                                        <p>Trial Balance at end of
                                            <a href="/reporting/reports/TrialBalance/?date=2013-12-31">2013</a>,
                                            <a href="/reporting/reports/TrialBalance/?date=2014-12-31">2014</a>,
                                            <a href="/reporting/reports/TrialBalance/?date=2015-12-31">2015</a>,
                                            <a href="/reporting/reports/TrialBalance/?date=2016-12-31">2016</a>,
                                            <a href="/reporting/reports/TrialBalance/?date=end_of_last_month">End of Last Month</a>,
                                            <a href="/reporting/reports/TrialBalance/?date=today">Today</a>
                                        </p>

                                        <p>Account Activity summary for
                                            <a href="/reporting/reports/AccountActivity/?col_tag=2013Annual">2013</a>,
                                            <a href="/reporting/reports/AccountActivity/?col_tag=2014Annual">2014</a>,
                                            <a href="/reporting/reports/AccountActivity/?col_tag=2015Annual">2015</a>,
                                            <a href="/reporting/reports/AccountActivity/?col_tag=current_YTD">2016 YTD</a>,
                                            <a href="/reporting/reports/AccountActivity/?col_tag=current_MTD">MTD</a>,
                                            <a href="/reporting/reports/AccountActivity/?col_tag=current_QTD">QTD</a>
                                        </p>
                                        
                                        <p>Cashflow statement for
                                            <a href="/reporting/reports/Cashflow/?col_tag=2014Annual">Annual 2014</a>,
                                            <a href="/reporting/reports/Cashflow/?col_tag=2015Monthly">Monthly 2015</a>,
                                            <a href="/reporting/reports/Cashflow/?col_tag=2015Annual">Annual 2015</a>,
                                            <a href="/reporting/reports/Cashflow/?col_tag=2016Monthly">2016</a>,
                                            <a href="/reporting/reports/Cashflow/?col_tag=12Mtrailing">Trailing 12 months</a>
                                        </p>

                                        <p>Income statement for
                                            <a href="/reporting/reports/IncomeStatement/?col_tag=2013Annual">2013</a>,
                                            <a href="/reporting/reports/IncomeStatement/?col_tag=2014Annual">2014</a>,
                                            <a href="/reporting/reports/IncomeStatement/?col_tag=2015Annual">2015</a>,
                                            <a href="/reporting/reports/IncomeStatement/?col_tag=2016Monthly">Monthly 2016</a>,
                                            <a href="/reporting/reports/IncomeStatement/?col_tag=12Mtrailing">Trailing 12 months</a>
                                        </p>

                                        <p>Balance Sheet as of
                                            <a href="/reporting/reports/BalanceSheet/?col_tag=2013Annual">2013</a>,
                                            <a href="/reporting/reports/BalanceSheet/?col_tag=2014Annual">2014</a>,
                                            <a href="/reporting/reports/BalanceSheet/?col_tag=2015Annual">2015</a>,
                                            <a href="/reporting/reports/BalanceSheet/?date=today">Today</a>
                                        </p>
                                    </div>    
                                </div>
                            </div>
                            
                            <div className="col-md-6">
                                <div className="panel panel-default">
                                    <div className="panel-heading">
                                        <h3 className="panel-title">Sales Tax</h3>
                                    </div>
                                    <div className="panel-body">
                                        <h3>Aggregated by collector</h3>
                                    <ul>
                                        <li>
                                            <a href="/api/reports/collected_salestax/?from_date=2016-6-1&to_date=2016-8-31">
                                                1-Jun-16 to 31-Aug-16
                                            </a>
                                        </li>
                                        <li>
                                            <a href="/api/reports/collected_salestax/?from_date=2016-3-1&to_date=2016-5-31">
                                                    1-Mar-16 to 31-May-16
                                            </a>
                                        </li>
                                    </ul>
                                    <h3>Download all salestax</h3>
                                    <ul>
                                        <li>
                                            <a href="/api/sales/salestax/?as_csv=true&from_date=2016-6-1&to_date=2016-8-31">
                                                1-Jun-16 to 31-Aug-16
                                            </a>
                                        </li>
                                        <li>
                                            <a href="/api/sales/salestax/?as_csv=true&from_date=2016-3-1&to_date=2016-5-31">
                                                    1-Mar-16 to 31-May-16
                                            </a>
                                        </li>
                                    </ul>
                                    <h3>Download all taxable sales</h3>
                                    <ul>
                                        <li>
                                            <a href="/api/sales/salestax2/?as_csv=true&from_date=2016-6-1&to_date=2016-8-31">
                                                1-Jun-16 to 31-Aug-16
                                            </a>
                                        </li>
                                        <li>
                                            <a href="/api/sales/salestax2/?as_csv=true&from_date=2016-3-1&to_date=2016-5-31">
                                                    1-Mar-16 to 31-May-16
                                            </a>
                                        </li>
                                    </ul>
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

export default connect(mapStateToProps)(ReportsView);
export { ReportsView as ReportsViewNotConnected };
