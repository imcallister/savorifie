import React from 'react';
import { Link } from 'react-router';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { push } from 'react-router-redux';
import { authLogoutAndRedirect } from './actions/auth';
import classNames from 'classnames';

import injectTapEventPlugin from 'react-tap-event-plugin';
injectTapEventPlugin();

import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';

import IconMenu from 'material-ui/IconMenu';
import IconButton from 'material-ui/IconButton';
import FontIcon from 'material-ui/FontIcon';
import MenuIcon from 'material-ui/svg-icons/navigation/menu';

import NavigationExpandMoreIcon from 'material-ui/svg-icons/navigation/expand-more';
import MenuItem from 'material-ui/MenuItem';
import DropDownMenu from 'material-ui/DropDownMenu';
import RaisedButton from 'material-ui/RaisedButton';
import {Toolbar, ToolbarGroup, ToolbarSeparator, ToolbarTitle} from 'material-ui/Toolbar';


import savorLogo from './shared/images/savor-logo.png';
import MenuBar from './shared/components/MenuBar';

import './styles/main.scss';

const styles = {
  mediumSize: {
    height: '80%',
  },
};

const routeLabels = {
    '': 'Home',
    'fulfillment': 'Fulfillment',
    'inventory': 'Inventory',
    'analysis': 'Analysis',
    'logout': 'Logout'
}

class App extends React.Component {

    static propTypes = {
        isAuthenticated: React.PropTypes.bool.isRequired,
        children: React.PropTypes.shape().isRequired,
        dispatch: React.PropTypes.func.isRequired,
        pathName: React.PropTypes.string.isRequired
    };

    constructor(props) {
        super(props);
        this.state = {
          route: '',
        };
    }

    handleRouteChange = (event, index) => {
        console.log('handling Route Change', index);
        this.setState({route: index});
        this.props.dispatch(push('/' + index));
    };


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
        const { actions } = this.props;
        
        const homeClass = classNames({
            active: this.props.pathName === '/'
        });

        const fulfillmentClass = classNames({
            active: this.props.pathName === '/fulfillment'
        });

        const loginClass = classNames({
            active: this.props.pathName === '/login'
        });

        return (
            <div>
                <MenuBar/>
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
                                    null}
                            </ToolbarGroup>
                            <ToolbarGroup>
                              <img className="page-logo margin-bottom-medium margin-top-medium"
                                     src={savorLogo}
                                     style={styles.mediumSize}
                                     alt="Savor"
                                />
                            </ToolbarGroup>
                            
                          </Toolbar>

                        <div>
                            {this.props.children}
                        </div>
                    </div>
                    
                </MuiThemeProvider>
            </div>
        );
    }
}


function mapStateToProps(state, ownProps) {
    return {
        isAuthenticated: state.auth.isAuthenticated,
        pathName: ownProps.location.pathname
    };
}


export default connect(mapStateToProps)(App);


