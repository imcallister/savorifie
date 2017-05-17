import React, { Component } from 'react';
import { Link } from 'react-router';
import { push } from 'react-router-redux';
import { connect } from 'react-redux';
import { authLogoutAndRedirect } from '../../actions/auth';
import classNames from 'classnames';

import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import {blue500, red500, greenA200} from 'material-ui/styles/colors';
import ExitToApp from 'material-ui/svg-icons/action/exit-to-app';

import Drawer from 'material-ui/Drawer';
import MenuItem from 'material-ui/MenuItem';
import IconMenu from 'material-ui/IconMenu';
import IconButton from 'material-ui/IconButton';
import MenuIcon from 'material-ui/svg-icons/navigation/menu';
import {Toolbar, ToolbarGroup, ToolbarTitle} from 'material-ui/Toolbar';

import savorLogo from '../images/savor-logo.png';

import '../../styles/main.scss';

const styles = {
  mediumSize: {
    height: '100%',
  },
};

const iconStyles = {
  marginRight: 24,
};

const routeLabels = {
    '': 'Home',
    'fulfillment': 'Fulfillment',
    'inventory': 'Inventory',
    'analysis': 'Analysis',
    'logout': 'Logout'
}


class MenuBar2 extends Component {

      constructor(props) {
        super(props);
        this.state = {open: false};
      }

    handleToggle = () => this.setState({open: !this.state.open});

    handleRouteChange = (event, index) => {
        if (index == 'logout') {
            this.props.dispatch(authLogoutAndRedirect());
        }
        else {
            this.setState({route: index});
            this.props.dispatch(push('/' + index));    
        }
    };

	render() {
        return (
                <MuiThemeProvider>
                    <div>
                        <Toolbar>
                            <ToolbarGroup firstChild={true}>
                                {this.props.isAuthenticated ?
                                    <div>
                                    <IconMenu
                                      iconButtonElement={<IconButton><MenuIcon /></IconButton>}
                                      onChange={this.handleRouteChange}
                                      value={this.state.valueSingle}
                                    >
                                        <MenuItem value="" primaryText="Home" />
                                        <MenuItem value="fulfillment" primaryText="Fulfillment" />
                                        <MenuItem value="inventory" primaryText="Inventory" />
                                        <MenuItem value="analysis" primaryText="Analysis" />
                                        <MenuItem value="logout" primaryText="Logout" />
                                    </IconMenu>
                                    <ToolbarTitle text={routeLabels[this.state.route]} />
                                    </div>
                                    :
                                    <ul className={classNames("nav", "navbar-nav", "navbar-right")}>
                                        <li className={this.props.loginClass}>
                                            <Link className="js-login-button" to="/login">Login</Link>
                                        </li>
                                    </ul>
                                }
                            </ToolbarGroup>
                            <ToolbarGroup>
                              <img className="page-logo"
                                     src={savorLogo}
                                     style={styles.mediumSize}
                                     alt="Savor"
                                />
                            </ToolbarGroup>
                            <ToolbarGroup>
                              <ExitToApp style={iconStyles} />
                            </ToolbarGroup>
                            
                          </Toolbar>
                    </div>
                    
                </MuiThemeProvider>
        );
	}
}

function mapStateToProps(state, ownProps) {
    return {
        isAuthenticated: state.auth.isAuthenticated,
    };
}


export default connect(mapStateToProps)(MenuBar2);		