
import 'babel-polyfill';
import React from 'react';
import { render } from 'react-dom';
import { browserHistory } from 'react-router';
import { syncHistoryWithStore } from 'react-router-redux';

import Root from './shared/containers/Root';
import configureStore from './store/configureStore';
import { authLoginUserSuccess } from './actions/auth';


const target = document.getElementById('root');

const store = configureStore(window.INITIAL_STATE, browserHistory);
const history = syncHistoryWithStore(browserHistory, store);

const node = (
    <Root store={store} history={history}/>
);

const token = sessionStorage.getItem('token');
let user = {};
try {
    user = JSON.parse(sessionStorage.getItem('user'));
} catch (e) {
    // Failed to parse
}

if (token !== null) {
    store.dispatch(authLoginUserSuccess(token, user));
}

render(node, target);
