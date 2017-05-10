import React from 'react';
import { Link } from 'react-router';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import SelectField from 'material-ui/SelectField';
import MenuItem from 'material-ui/MenuItem';
import {Tabs, Tab} from 'material-ui/Tabs';

import {Grid, Row, Col} from 'react-bootstrap';
import Dropzone from 'react-dropzone';

import OrderUpload from './components/OrderUpload';
import IncompleteOrders from './components/IncompleteOrders';

import savorLogo from '../shared/images/savor-logo.png';

import Drawer from 'material-ui/Drawer';
import IconButton from 'material-ui/IconButton';
import MenuIcon from 'material-ui/svg-icons/navigation/menu';

import * as CPartyActions from '../actions/cparty';
import * as IncompleteSalesActions from '../actions/incompletesales';



const styles = {
  largeIcon: {
    width: 40,
    height: 40,
  },
  padding: {
    'paddingTop': '0.5cm',
    'paddingBottom': '0.5cm'
  }

};

class FulfillmentView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {open: false};
      }

    componentWillMount() {
        this.props.actions.getCounterparties(this.props.token);
        this.props.actions.getIncompleteSales(this.props.token);
    }
  

    handleToggle = () => this.setState({open: !this.state.open});

    static propTypes = {
        statusText: React.PropTypes.string,
        userName: React.PropTypes.string
    };

    render() {
        const { incompleteList } = this.props;
        return (
            <div className="container-fluid" style={styles.padding}>
                <Tabs>
                    <Tab label="Upload Orders">
                        <div className={'panel panel-default'}>
                            <div className={'panel-body'}>
                                <OrderUpload />
                            </div>
                        </div>
                    </Tab>
                    <Tab label="Incomplete Orders">
                        <IncompleteOrders cpartyList={this.props.cpartyList}
                                          incompleteList={incompleteList} 
                                          actions={this.props.actions}
                        />
                    </Tab>
                    <Tab label="Send to Warehouse">
                        <div className="text-center">
                            <h1>And this is where we do fulfillment part III</h1>
                        </div>
                        {this.props.isAuthenticated ?
                            <div className="margin-top-medium text-center">
                                <p><Link to="/login"><b>Login to access application</b></Link>.</p>
                            </div>
                            :
                            null
                        }
                    </Tab>
                </Tabs>
            </div>
            
        );
    }
}

const mapStateToProps = (state) => {
    return {
        userName: state.auth.userName,
        statusText: state.auth.statusText,
        token: state.auth.token,
        cpartyList: state.cparty.data,
        incompleteList: state.incompletesales.data
    };
};

function mapDispatch(dispatch) {
  return {
    actions: bindActionCreators(Object.assign({}, CPartyActions, IncompleteSalesActions), dispatch)
  };
}


export default connect(mapStateToProps, mapDispatch)(FulfillmentView);
export { FulfillmentView as FulfillmentViewNotConnected };
