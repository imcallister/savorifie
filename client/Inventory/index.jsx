import React from 'react';
import { Link } from 'react-router';
import { connect } from 'react-redux';

import savorLogo from '../shared/images/savor-logo.png';

class InventoryView extends React.Component {

    static propTypes = {
        statusText: React.PropTypes.string,
        userName: React.PropTypes.string
    };

    render() {
        return (
            <div className="container">
                <div className="margin-top-medium text-center">
                    <img className="page-logo margin-bottom-medium"
                         src={savorLogo}
                         alt="Savor"
                    />
                </div>
                <div className="text-center">
                    <h1>And this is where we do Inventory</h1>
                </div>
                {this.props.isAuthenticated ?
                    <div className="margin-top-medium text-center">
                        <p><Link to="/login"><b>Login to access application</b></Link>.</p>
                    </div>
                    :
                    null
                }
            </div>
        );
    }
}

const mapStateToProps = (state) => {
    return {
        userName: state.auth.userName,
        statusText: state.auth.statusText
    };
};

export default connect(mapStateToProps)(InventoryView);
export { InventoryView as InventoryViewNotConnected };
