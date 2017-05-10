import React from 'react';
import { Route, IndexRoute } from 'react-router';
import App from './app';

import AnalysisView from './Analysis'
import FulfillmentView from './Fulfillment'
import HomeView from './Home'
import InventoryView from './Inventory'
import LoginView from './Login'
import NotFoundView from './NotFound'

import requireAuthentication from './utils/requireAuthentication';

export default(
    <Route path="/" component={App}>
        <IndexRoute component={HomeView}/>
        <Route path="login" component={LoginView}/>
        <Route path="fulfillment" component={FulfillmentView}/>
        <Route path="inventory" component={InventoryView}/>
        <Route path="analysis" component={AnalysisView}/>
        <Route path="*" component={HomeView}/>
    </Route>
);
