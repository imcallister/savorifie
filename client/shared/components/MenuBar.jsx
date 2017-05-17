import React, { Component } from 'react';
import { Link } from 'react-router';
import { push } from 'react-router-redux';
import { connect } from 'react-redux';
import classNames from 'classnames';

import { authLogoutAndRedirect } from '../../actions/auth';

import Drawer from 'material-ui/Drawer';
import MenuItem from 'material-ui/MenuItem';
import RaisedButton from 'material-ui/RaisedButton';


import savorLogo from '../images/savor-logo.png';

import '../../styles/main.scss';


class MenuBar extends Component {

      constructor(props) {
        super(props);
        this.state = {open: false};
      }

     handleToggle = () => this.setState({open: !this.state.open});

    goToIndex = () => {
        this.props.dispatch(push('/'));
    };

    goToFulfillment = () => {
        this.props.dispatch(push('/fulfillment'));
    };

    goToInventory = () => {
        this.props.dispatch(push('/inventory'));
    };

    goToAnalysis = () => {
        this.props.dispatch(push('/analysis'));
    };

    
    logout = () => {
        this.props.dispatch(authLogoutAndRedirect());
    };


	render() {
        return (
            <nav className={classNames("navbar", "navbar-default")}>
                <div className="container-fluid">
                    <div className="navbar-header">
                        <Link to="/">
                            <img className="navbar-logo"
                                 src={savorLogo}
                                 alt="savor"
                            />
                        </Link>
                    </div>
                    <div className={classNames("collapse", "navbar-collapse")} id="top-navbar">
                        
                        {this.props.isAuthenticated ?
                            <ul className={classNames("nav", "navbar-nav", "navbar-right")}>
                                <li>
                                    <a className="js-go-to-index-button" 
                                        tabIndex="0"
                                        onClick={this.goToInventory}>
                                        <i className="fa fa-home"/> Inventory
                                    </a>
                                </li>
                                <li>
                                    <a className="js-go-to-index-button" 
                                        tabIndex="0"
                                        onClick={this.goToFulfillment}>
                                        <i className="fa fa-home"/> Fulfillment
                                    </a>
                                </li>
                                <li>
                                    <a className="js-go-to-index-button" 
                                        tabIndex="0"
                                        onClick={this.goToAnalysis}>
                                        <i className="fa fa-home"/> Analysis
                                    </a>
                                </li>
                                <li>
                                    <a className="js-logout-button"
                                       tabIndex="0"
                                       onClick={this.logout}>
                                        Logout
                                    </a>
                                </li>
                            </ul>
                        :
                            <ul className={classNames("nav", "navbar-nav", "navbar-right")}>
                                <li>
                                    <a className="js-go-to-index-button" tabIndex="0" onClick={this.props.goToIndex}>
                                        <i className="fa fa-home"/> Home
                                    </a>
                                </li>
                                <li className={this.props.loginClass}>
                                    <Link className="js-login-button" to="/login">Login</Link>
                                </li>
                            </ul>
                        }
                    </div>
                    
                </div>
            </nav>
        );
	}
}

function mapStateToProps(state, ownProps) {
    return {
        isAuthenticated: state.auth.isAuthenticated,
    };
}


export default connect(mapStateToProps)(MenuBar);		