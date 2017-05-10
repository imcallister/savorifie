import _ from 'underscore';

import React, {Component} from 'react';
import { connect } from 'react-redux';

import AutoComplete from 'material-ui/AutoComplete';
import FlatButton from 'material-ui/FlatButton';
import {List, ListItem} from 'material-ui/List';

import {TableRow, TableRowColumn} from 'material-ui/Table';
import Table from '../../shared/components/Table';

class IncompleteOrderRow extends Component {
    
    constructor(props) {
    	super(props);
    	this.state = {'cp': ''};
    }

    handleChange(cpName) {
    	this.setState({'cp': cpName});
    }

    onSave() {
    	var token = '';
    	var cpId = _.findWhere(this.props.cpartyList, {name: this.state.cp}).id;
    	this.props.patchOrder(token, this.props.orderId, {'customer_code': cpId});
    }

	render() {
		const rowKey=this.props.label;
	    return (
	    	<TableRow selectable={true} key={rowKey}>
	        	<TableRowColumn key={rowKey+'label'}>{this.props.label}</TableRowColumn>
	        	<TableRowColumn key={rowKey+'CP'}>
	        		<AutoComplete
						floatingLabelText="Enter customer code"
						searchText={''}
						filter={AutoComplete.caseInsensitiveFilter}
						dataSource={this.props.cpartyList.map((e => e.name))}
						onUpdateInput={((v) => this.handleChange(v))}
					/>
	        	</TableRowColumn>
	        	<TableRowColumn key={rowKey+'save'}>
	        		<FlatButton label="Save" secondary={true} onClick={() => this.onSave()} />
	        	</TableRowColumn>
	        </TableRow>
	    )
	}
}



class IncompleteOrders extends Component {

	makeRow(r, i) {
		return (
			<IncompleteOrderRow  key={'IncompleteOrderRow'+r.label}
								 label={r.label}
								 orderId={r.id}
								 cpartyList={this.props.cpartyList}
								 patchOrder={this.props.actions.patchIncompleteSales}
			/>
		)
		
	}

	render() {
		var rows = this.props.incompleteList.map((r, i) => this.makeRow(r, i))
		return (
			<div className={'panel panel-default'}>
	            <div className={'panel-body'}>
	            	{this.props.loading ?
	            		<h3>...Loading...</h3>
	            		:
	            		<div>
			            	{this.props.incompleteList.length == 0 ?
			            		<h3>There are no incomplete orders</h3>
			            		:
			            		<Table key='incompletesales'
			            			   headers={['Order', 'Customer Code', '']}
			            			   rows={rows}/>
			            	}
			            </div>
		            }
	             </div>
			</div>
		);
	}
}

const mapStateToProps = (state) => {
    return {
        cpartyList: state.cparty.data,
        incompleteList: state.incompletesales.data,
        loading: state.incompletesales.isFetchingIncompleteSales
    };
};


export default connect(mapStateToProps)(IncompleteOrders);
