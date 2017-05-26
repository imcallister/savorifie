import React, { Component } from 'react';
import { Link } from 'react-router';
import { push } from 'react-router-redux';
import { connect } from 'react-redux';
import { authLogoutAndRedirect } from '../../actions/auth';

import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import {blue500, red500, greenA200} from 'material-ui/styles/colors';
import ExitToApp from 'material-ui/svg-icons/action/exit-to-app';

import Drawer from 'material-ui/Drawer';
import MenuItem from 'material-ui/MenuItem';
import IconMenu from 'material-ui/IconMenu';
import IconButton from 'material-ui/IconButton';
import MenuIcon from 'material-ui/svg-icons/navigation/menu';
import {Toolbar, ToolbarGroup, ToolbarTitle} from 'material-ui/Toolbar';
import Divider from 'material-ui/Divider';

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
    'finance/reports': 'Finance / Reporting',
    'finance/payables': 'Finance / Payables',
    'fulfillment': 'Fulfillment',
    'inventory': 'Inventory',
    'analysis': 'Analysis',
    'logout': 'Logout'
}


class MenuDrawer extends Component {

      constructor(props) {
        super(props);
        this.state = {open: false};
      }

    handleToggle = () => this.setState({open: !this.state.open});
    
    handleClose = (index, serverFlag) => {
        console.log('MenuDrawer, index:', index, serverFlag)
        
        if (serverFlag == true) {
            console.log('coming into serverFlag');
            console.log(window);
            window.location.replace('/' + index);
        };

        this.setState({open: false, route: index});
        this.props.dispatch(push('/' + index));
    }

    handleLogout = (event) => {
        this.props.dispatch(authLogoutAndRedirect());
    };

	render() {
        return (
                <MuiThemeProvider>
                    <Toolbar>
                        <ToolbarGroup>
                            {this.props.isAuthenticated ?
                                <div>
                                    
                                    <div className="row">
                                        <MenuIcon style={iconStyles} onTouchTap={this.handleToggle}/>
                                        <ToolbarTitle text={routeLabels[this.state.route]} />
                                    </div>

                                    
                                    
                                      <Drawer 
                                        open={this.state.open}
                                        docked={false}
                                        width={250}
                                        onRequestChange={(open) => this.setState({open})}
                                      >
                                        <MenuItem onTouchTap={this.handleClose.bind(this, "")}>Home</MenuItem>
                                        <Divider />
                                        <MenuItem onTouchTap={this.handleClose.bind(this, "finance/reports")}>Financial Reporting</MenuItem>
                                        <MenuItem onTouchTap={this.handleClose.bind(this, "finance/payables")}>Banks & Payables</MenuItem>
                                        <MenuItem onTouchTap={this.handleClose.bind(this, "finance/receivables")}>Receivables</MenuItem>
                                        <MenuItem onTouchTap={this.handleClose.bind(this, "finance/shipping")}>Shipping Costs</MenuItem>
                                        <Divider />
                                        <MenuItem onTouchTap={this.handleClose.bind(this, "inventory/counts")}>Inventory Counts</MenuItem>
                                        <MenuItem onTouchTap={this.handleClose.bind(this, "inventory/loadorders")}>Load Orders</MenuItem>
                                        <MenuItem onTouchTap={this.handleClose.bind(this, "inventory/fulfillment")}>Fulfillment</MenuItem>
                                        <MenuItem onTouchTap={this.handleClose.bind(this, "inventory/warehouserec")}>Warehouse Reconciliation</MenuItem>
                                        <Divider />
                                        <MenuItem onTouchTap={this.handleClose.bind(this, "analysis")}>Analysis</MenuItem>
                                        <Divider />
                                        <MenuItem onTouchTap={this.handleClose.bind(this, "admin/", true)}>Admin</MenuItem>
                                        <MenuItem onTouchTap={this.handleClose.bind(this, "superuser/maintenance/", true)}>Maintenance</MenuItem>
                                        <MenuItem onTouchTap={this.handleClose.bind(this, "superuser/logs/", true)}>Logs</MenuItem>
                                      </Drawer>
                                    
                                   
                                </div>
                                :
                                <ul className="nav navbar-nav navbar-right">
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
                            <IconButton style={iconStyles} onTouchTap={this.handleLogout} tooltip="Logout">
                                <ExitToApp/>
                            </IconButton>
                        </ToolbarGroup>
                        
                      </Toolbar>
                    
                    
                </MuiThemeProvider>
        );
	}
}

function mapStateToProps(state, ownProps) {
    return {
        isAuthenticated: state.auth.isAuthenticated,
    };
}


export default connect(mapStateToProps)(MenuDrawer);		