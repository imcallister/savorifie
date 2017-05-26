import React from 'react';
import { Route, IndexRoute } from 'react-router';
import App from './app';

import AnalysisView from './Analysis'
import FulfillmentView from './Fulfillment'
import HomeView from './Home'
import InventoryView from './Inventory'
import LogsView from './Superuser/logs'
import MaintenanceView from './Superuser/maintenance'
import LoginView from './Login'
import NotFoundView from './NotFound'
import ReportsView from './Finances/reports'
import PayablesView from './Finances/payables'
import HistoryView from './History'

import requireAuthentication from './utils/requireAuthentication';

export default(
    <Route path="/" component={App}>
        <IndexRoute component={HomeView}/>
        <Route path="login" component={LoginView}/>
        <Route path="fulfillment" component={FulfillmentView}/>
        <Route path="inventory" component={InventoryView}/>
        <Route path="analysis" component={AnalysisView}/>
        <Route path="finance">
            <Route path="receivables" component={ReportsView}/>
            <Route path="reports" component={ReportsView}/>
            <Route path="payables" component={PayablesView}/>
            <Route path="shipping" component={PayablesView}/>
        </Route>
        <Route path="superuser" component={LogsView}>
            <Route path="logs" component={LogsView}/>
            <Route path="maintenance" component={MaintenanceView}/>
        </Route>
        
        <Route path="history" component={HistoryView}/>
        
    </Route>
);
