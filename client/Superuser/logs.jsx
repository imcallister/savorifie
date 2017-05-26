import React from 'react';
import { Link } from 'react-router';
import { connect } from 'react-redux';
import classNames from 'classnames';

import HighChartContainer from '../shared/containers/HighChart';
import ModalContainer from '../shared/containers/Modal';
import UploadContainer from '../shared/containers/UploadContainer';
import TableContainer from '../shared/containers/TableContainer';
import SwatchRow from '../shared/containers/swatchRowContainer';
import { SERVER_URL } from '../utils/config';

import formatters from '../shared/helpers/formatters';

import MCardHelp  from '../help_text/MCard_upload';
import FRBHelp  from '../help_text/FRB_upload';


import '../styles/main.scss';
import savorLogo from '../shared/images/savor-logo.png';



class LogsView extends React.Component {

    static propTypes = {
        statusText: React.PropTypes.string,
        userName: React.PropTypes.string
    };


    render() {
        return (
            
            <div className="container">
                {this.props.isAuthenticated ?
                    <div>
                        <div className={classNames("panel", "panel-default")}>
                            <div className="panel-heading">
                                <h3 className="panel-title">Incomplete Entries</h3>
                            </div>
                            <div className="panel-body">
                                <div>
                                    <SwatchRow config={SWATCH_COLORS} source='/api/reports/incompletes/?raw=true' />
                                </div>
                            </div>
                        </div>
                        
                        <div className="row">
                            <div className="col-md-8">  
                                <div className={classNames("panel", "panel-default")}>
                                    <div className="panel-heading">
                                        <h3 className="panel-title">Payables</h3>
                                    </div>
                                    <div className="panel-body">
                                        <div>
                                            <TableContainer source='${SERVER_URL}/api/reports/payables/?raw=true' headers={payables_headers}/>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="col-md-4">  
                                <div className={classNames("panel", "panel-default")}>
                                    <div className="panel-heading">
                                        <h3 className="panel-title">File Uploads</h3>
                                    </div>
                                    <div className="panel-body">
                                        <div>
                                           <TableContainer source='${SERVER_URL}/api/reports/last_uploads/?raw=true' headers={last_upload_headers}/>
                                        </div>
                                    </div>
                                </div>
                                <div className={classNames("panel", "panel-default")}>
                                    <div className="panel-heading">
                                        <h3 className="panel-title">Uploads</h3>
                                    </div>
                                    <div className={classNames('panel-body', 'text-center')}>
                                        <div>
                                            <ul className="nav nav-pills nav-stacked">
                                                <li><ModalContainer title="Load FRB" content={<UploadContainer instructions={<FRBHelp/>} postUrl={'/importers/upload/frb/'}/>}/></li>
                                                <li><ModalContainer title="Load Mastercard" content={<UploadContainer instructions={<MCardHelp/>} postUrl={'/importers/upload/mcard/'}/>}/></li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </div>
            
                            
                        </div>
                    </div>
                
                    :
                    <div className={classNames("margin-top-medium", "text-center")}>
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
        token: state.auth.token,
        isAuthenticated: state.auth.isAuthenticated
    };
};



export default connect(mapStateToProps)(LogsView);
export { LogsView as LogsViewNotConnected };
