import React, {Component} from 'react';
import {Grid, Row, Col} from 'react-bootstrap';

import SelectField from 'material-ui/SelectField';
import MenuItem from 'material-ui/MenuItem';

import Dropzone from 'react-dropzone';
import Uploader from '../../shared/containers/UploadContainer';

var shopifyInstructions = <div>
                            Expects a csv file with at least following headers:
                            <ul>
                                <li>Date</li>
                                <li>Amount Debit</li>
                                <li>Amount Credit</li>
                                <li>Description</li>
                                <li>Transaction Number</li>
                            </ul>
                            It is currently confgured to expect the headers row to be on row 4.
                        </div>

var buybuyInstructions = <div>
                            Expects a csv file with at least following headers:
                            <ul>
                                <li>Date</li>
                                <li>Transaction Number</li>
                            </ul>
                            It is currently confgured to expect the headers row to be on row 4.
                        </div>


export default class OrderUpload extends Component {

    constructor() {
    super();
    }

    state = {
        value: 1,
    };

    handleChange = (event, index, value) => this.setState({value});

    dropzone() {
        switch (this.state.value) {
            case 1:
                return <Uploader lbl='shopifyUploader' instructions={shopifyInstructions} postUrl={'/importers/upload/shopify/'}/>
            case 2:
                return <Uploader lbl='buybuyUploader' instructions={buybuyInstructions} postUrl={'/importers/upload/buybuy/'}/>
        }
    }

    render() {
        return (
            <div>
                <Grid>
                    <Row>
                        <Col md={4}>
                            <SelectField
                                floatingLabelText="Source"
                                value={this.state.value}
                                onChange={this.handleChange}
                            >
                              <MenuItem value={1} primaryText="Shopify" />
                              <MenuItem value={2} primaryText="Buy-Buy" />
                            </SelectField>
                        </Col>
                        <Col md={8} className={'col-centered'}>
                            {this.dropzone()}
                        </Col>
                    </Row>
                </Grid>
            </div>
        );
    }
}