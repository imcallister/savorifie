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


import MenuBar from './shared/components/MenuBar';
import MenuBar2 from './shared/components/MenuBar2';

import './styles/main.scss';

const styles = {
  mediumSize: {
    height: '80%',
  },
};


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

    render() {
        const { actions } = this.props;
        return (
            <div>
                <MenuBar2/>
                <MuiThemeProvider>
                    <div>
                        {this.props.children}
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


